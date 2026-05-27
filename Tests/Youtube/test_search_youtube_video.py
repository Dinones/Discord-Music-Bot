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
from unittest.mock import AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Youtube
import Utils.Constants as CONST
from Utils.Music_Manager import Music_Manager
from Tests.Helpers.helpers import _build_test_message, _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Search_Youtube_Video(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self._music_manager = Music_Manager()
        self.message = _build_test_message()

    #######################################################################################################################
    #######################################################################################################################

    async def test_search_youtube_video_by_url_returns_shortest_result(self) -> None:

        """
        Test that search_youtube_video() returns the shortest video when searching by YouTube URL.
        """

        response = {
            "entries": [
                {"title": "Long", "duration": 300},
                {"title": "Short", "duration": 120}
            ]
        }

        with (
            patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(return_value = response))
        ):
            result = await Utils.Youtube.search_youtube_video(
                Music_Manager = self._music_manager,
                message       = self.message,
                args          = CONST.TESTING_YOUTUBE_LINK
            )

        self.assertIsNotNone(
            result,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should not return None for a valid response.'
            )
        )

        song_name = "Short"
        self.assertEqual(
            result.get("title"),
            song_name,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should have returned the shortest song name ' +
                f'"{song_name}" instead of "{result.get("title")}".'
            )
        )
        self.assertEqual(
            result.get("duration"),
            120,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should have returned the shortest song duration ' +
                f'"120" instead of "{result.get("duration")}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_search_youtube_video_by_query_appends_lyrics_and_uses_ytsearch2(self) -> None:

        """
        Test that search_youtube_video() appends 'lyrics' and uses ytsearch2 for text queries.
        """

        response = {
            "entries": [
                {"title": "Result", "duration": 100}
            ]
        }

        with (
            patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(return_value = response)) as mock_to_thread
        ):
            await Utils.Youtube.search_youtube_video(
                Music_Manager = self._music_manager,
                message       = self.message,
                args          = CONST.TESTING_YOUTUBE_QUERY
            )

        args = mock_to_thread.await_args.args
        ytdl_options = args[1]

        self.assertEqual(
            ytdl_options.get("default_search"),
            "ytsearch2",
            _color_error_message_in_red(
                f'The "default_search" value of "ytdl_options" should have been set to "ytsearch2" ' +
                f'instead of "{ytdl_options.get("default_search")}".'
            )
        )

        query = f"{CONST.TESTING_YOUTUBE_QUERY} lyrics"
        self.assertEqual(
            args[2],
            query,
            _color_error_message_in_red(
                f'The query argument of the "ytdl.extract_info()" function should have been "{query}" ' +
                f'instead of "{args[2]}".'
            )
        )

        self.assertFalse(
            args[3],
            _color_error_message_in_red(
                f'The "download" argument of the "ytdl.extract_info()" function should have been "False" ' +
                f'instead of "{args[3]}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_search_youtube_video_returns_none_for_empty_input(self) -> None:

        """
        Test that search_youtube_video() returns None for blank input.
        """

        with (
            patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock())
        ):
            result = await Utils.Youtube.search_youtube_video(
                Music_Manager = self._music_manager,
                message       = self.message,
                args          = "   "
            )

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "search_youtube_video()" function should have returned "None" ' +
                f'instead of "{result}" when no results are found in the Youtube search.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_search_youtube_video_returns_none_when_response_is_empty(self) -> None:

        """
        Test that search_youtube_video() returns None when extractor response has no entries and no title.
        """

        with (
            patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(return_value = {}))
        ):
            result = await Utils.Youtube.search_youtube_video(
                Music_Manager = self._music_manager,
                message       = self.message,
                args          = CONST.TESTING_YOUTUBE_QUERY
            )

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "search_youtube_video()" function should have returned "None" ' +
                f'instead of "{result}" when no results are found in the Youtube search.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_search_youtube_video_returns_none_on_download_error(self) -> None:

        """
        Test that search_youtube_video() returns None when a DownloadError is raised.
        """

        error = "An error occurred when trying to donwload the video from Youtube"

        with (
            patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(side_effect = Utils.Youtube.DownloadError(error))),
            patch("Utils.Youtube.save_exception_to_txt") as mock_save_exception
        ):
            result = await Utils.Youtube.search_youtube_video(
                Music_Manager = self._music_manager,
                message       = self.message,
                args          = CONST.TESTING_YOUTUBE_QUERY
            )

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "search_youtube_video()" function should have returned "None" ' +
                f'instead of "{result}" when no results are found in the Youtube search.'
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

    #######################################################################################################################
    #######################################################################################################################

    def test_extract_query_search_result_fully_extracts_shortest_flat_entry(self) -> None:

        """
        Test that _extract_query_search_result() fully extracts only the shortest flat search entry.
        """

        ytdl_options = {"default_search": "ytsearch2"}

        flat_response = {
            "entries": [
                {"id": "long-video", "duration": 300},
                {"id": "short-video", "duration": 120}
            ]
        }

        full_response = {"id": "short-video", "title": "Short"}

        with (
            patch("Utils.Youtube._extract_info", side_effect = [flat_response, full_response]) as mock_extract
        ):
            result = Utils.Youtube._extract_query_search_result(
                ytdl_options = ytdl_options,
                query        = "song lyrics",
                download     = False
            )

        self.assertEqual(
            result,
            full_response,
            _color_error_message_in_red(
                f'The "_extract_query_search_result()" function should return the fully extracted shortest result.'
            )
        )

        first_options = mock_extract.call_args_list[0].args[0]
        second_options = mock_extract.call_args_list[1].args[0]

        self.assertEqual(
            first_options.get("extract_flat"),
            "in_playlist",
            _color_error_message_in_red(
                f'The first extraction should use "extract_flat" to avoid fully extracting every search result.'
            )
        )

        self.assertEqual(
            second_options.get("default_search"),
            "auto",
            _color_error_message_in_red(
                f'The selected video extraction should use "auto" search mode.'
            )
        )

        self.assertEqual(
            mock_extract.call_args_list[1].args[1],
            "https://www.youtube.com/watch?v=short-video",
            _color_error_message_in_red(
                f'The selected video URL should be built from the shortest flat entry id.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
