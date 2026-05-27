###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Youtube
import Utils.Constants as CONST
from Utils.Music_Manager import Music_Manager
from Tests.Helpers.helpers import _build_test_message, _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Download_MP3(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self._music_manager = Music_Manager()
        self.message = _build_test_message()

    #######################################################################################################################
    #######################################################################################################################

    async def test_download_mp3_returns_filename_on_success(self) -> None:

        """
        Test that download_mp3() returns '<title>.mp3' when extraction succeeds.
        """

        response = {"title": "My Song"}

        with patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(return_value = response)) as mock_to_thread:
            result = await Utils.Youtube.download_mp3(
                Music_Manager = self._music_manager,
                message       = self.message,
                youtube_url   = CONST.TESTING_YOUTUBE_LINK,
                output_path   = CONST.TESTING_MP3_DOWNLOAD_OUTPUT_PATH
            )

        expected_output_path = Path(
            os.path.join(
                CONST.TESTING_MP3_DOWNLOAD_OUTPUT_PATH,
                f"{response.get('title')}.mp3")
            ).resolve().as_uri()
        self.assertEqual(
            result,
            expected_output_path,
            _color_error_message_in_red(
                f'The MP3 output path "{result}" does not match the expected one "{expected_output_path}".'
            )
        )

        to_thread_args = mock_to_thread.await_args.args
        ytdl_options = to_thread_args[1]

        self.assertFalse(
            ytdl_options.get("skip_download"),
            _color_error_message_in_red(
                f'Option "skip_download" of ytdl_options should be "False" instead ' +
                f'of "{ytdl_options.get("skip_download")}".'
            )
        )

        expected_output_path = os.path.join(CONST.TESTING_MP3_DOWNLOAD_OUTPUT_PATH, "%(title)s.%(ext)s")
        self.assertEqual(
            ytdl_options.get("outtmpl"),
            expected_output_path,
            _color_error_message_in_red(
                f'The MP3 ytdl_options output template "{ytdl_options.get("outtmpl")}" does not match the ' +
                f'expected one "{expected_output_path}".'
            )
        )

        self.assertTrue(
            to_thread_args[3],
            _color_error_message_in_red(
                f'Download argument is set to False in the "download_mp3()" funtion.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_download_mp3_returns_none_when_extractor_returns_empty_result(self) -> None:

        """
        Test that download_mp3() returns None when extraction returns an empty dictionary.
        """

        with patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(return_value = {})):
            result = await Utils.Youtube.download_mp3(
                Music_Manager = self._music_manager,
                message       = self.message,
                youtube_url   = CONST.TESTING_YOUTUBE_LINK,
                output_path   = CONST.TESTING_MP3_DOWNLOAD_OUTPUT_PATH
            )

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "download_mp3()" function should return "None" instead of "{result}" when no result is found.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_download_mp3_returns_none_on_download_error(self) -> None:
    
        """
        Test that download_mp3() returns None when yt-dlp raises DownloadError.
        """

        error = "An error occurred when trying to donwload the video from Youtube"

        with (
            patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(side_effect = Utils.Youtube.DownloadError(error))),
            patch("Utils.Youtube.save_exception_to_txt") as mock_save_exception
        ):
            result = await Utils.Youtube.download_mp3(
                Music_Manager = self._music_manager,
                message       = self.message,
                youtube_url   = CONST.TESTING_YOUTUBE_LINK,
                output_path   = CONST.TESTING_MP3_DOWNLOAD_OUTPUT_PATH
            )

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "download_mp3()" function should return "None" instead of "{result}" when the download fails.'
            )
        )

        self.assertEqual(
            mock_save_exception.call_count,
            1,
            _color_error_message_in_red(
                f'The "save_exception_to_txt()" function should have been called exactly "1" time instead of ' +
                f'"{mock_save_exception.call_count}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_download_mp3_returns_none_on_unexpected_error(self) -> None:

        """
        Test that download_mp3() returns None when an unexpected exception is raised.
        """

        error = "An error occurred when trying to donwload the video from Youtube"

        with (
            patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(side_effect = Exception(error))),
            patch("Utils.Youtube.save_exception_to_txt") as mock_save_exception
        ):
            result = await Utils.Youtube.download_mp3(
                Music_Manager = self._music_manager,
                message       = self.message,
                youtube_url   = CONST.TESTING_YOUTUBE_LINK,
                output_path   = CONST.TESTING_MP3_DOWNLOAD_OUTPUT_PATH
            )

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "download_mp3()" function should return "None" instead of ' +
                f'"{result}" when an unexpected error occurs.'
            )
        )

        self.assertEqual(
            mock_save_exception.call_count,
            1,
            _color_error_message_in_red(
                f'The "save_exception_to_txt()" function should have been called exactly "1" time(s) instead of ' +
                f'"{mock_save_exception.call_count}".'

            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
