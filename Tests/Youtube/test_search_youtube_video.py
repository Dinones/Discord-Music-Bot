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

        # Force asyncio.to_thread() to return response
        with patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(return_value = response)):
            result = await Utils.Youtube.search_youtube_video(self._music_manager, self.message, CONST.TESTING_YOUTUBE_LINK)

        # Check the result is not None
        self.assertIsNotNone(
            result,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should not return None for a valid response.'
            )
        )

        # Check it returned the shortest result (name and duration)
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

        response = {"entries": [{"title": "Result", "duration": 100}]}

        # Force asyncio.to_thread() to return response
        with patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(return_value = response)) as mock_to_thread:
            await Utils.Youtube.search_youtube_video(self._music_manager, self.message, CONST.TESTING_YOUTUBE_QUERY)

        args = mock_to_thread.await_args.args
        ytdl_options = args[1]

        # Check the default_search value is set to "ytsearch2"
        self.assertEqual(
            ytdl_options.get("default_search"),
            "ytsearch2",
            _color_error_message_in_red(
                f'The "default_search" value of "ytdl_options" should have been set to "ytsearch2" ' +
                f'instead of "{ytdl_options.get("default_search")}".'
            )
        )

        # Check the song query is the expected one with the word "lyrics" added at the end
        query = f"{CONST.TESTING_YOUTUBE_QUERY} lyrics"
        self.assertEqual(
            args[2],
            query,
            _color_error_message_in_red(
                f'The query argument of the "ytdl.extract_info()" function should have been "{query}" ' +
                f'instead of "{args[2]}".'
            )
        )

        # Check the download option is set to False
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

        # Force asyncio.to_thread() to return an AsyncMock object
        with patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock()):
            result = await Utils.Youtube.search_youtube_video(self._music_manager, self.message, "   ")

        # Check None is returned when no results are found in the Youtube search
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

        # Force asyncio.to_thread() to return {}
        with patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(return_value = {})):
            result = await Utils.Youtube.search_youtube_video(self._music_manager, self.message, CONST.TESTING_YOUTUBE_QUERY)

        # Check None is returned when no results are found in the Youtube search
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

        # Force asyncio.to_thread() to raise a DownloadError
        with patch("Utils.Youtube.asyncio.to_thread", new = AsyncMock(side_effect = Utils.Youtube.DownloadError(error))):
            result = await Utils.Youtube.search_youtube_video(self._music_manager, self.message, CONST.TESTING_YOUTUBE_QUERY)

        # Check None is returned when an error is raised
        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "search_youtube_video()" function should have returned "None" ' +
                f'instead of "{result}" when no results are found in the Youtube search.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)