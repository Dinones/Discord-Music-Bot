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
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Youtube
from Utils.Music_Manager import Music_Manager
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Get_Video_From_Spotify_Song(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self._music_manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    def test_get_video_from_spotify_song_returns_shortest_result(self) -> None:

        """
        Test that get_video_from_spotify_song() returns the shortest entry from search results.
        """

        response = {
            "entries": [
                {"title": "Long", "duration": 400},
                {"title": "Short", "duration": 120}
            ]
        }

        mock_ytdl_instance = Mock()
        mock_ytdl_instance.extract_info.return_value = response

        # Force YoutubeDL() to return mock_ytdl_instance
        with patch("Utils.Youtube.YoutubeDL") as mock_youtubedl:
            mock_youtubedl.return_value.__enter__.return_value = mock_ytdl_instance
            result = Utils.Youtube.get_video_from_spotify_song(
                Music_Manager = self._music_manager,
                song_title    = "Title",
                song_authors  = "Author"
            )

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

        # Get the arguments passed to ytdl.extract_info(args)
        extract_args = mock_ytdl_instance.extract_info.call_args.args
        ytdl_options = mock_youtubedl.call_args.args[0]

        # Check the song query is the expected one with the word "lyrics" added at the end
        query = "Title Author lyrics"
        self.assertEqual(
            extract_args[0],
            query,
            _color_error_message_in_red(
                f'The query argument of the "ytdl.extract_info()" function should have been "{query}" ' +
                f'instead of "{extract_args[0]}".'
            )
        )

        # Check the download option is set to False
        self.assertFalse(
            mock_ytdl_instance.extract_info.call_args.kwargs.get("download"),
            _color_error_message_in_red(
                f'The "download" argument of the "ytdl.extract_info()" function should have been "False" ' +
                f'instead of "{mock_ytdl_instance.extract_info.call_args.kwargs.get("download")}".'
            )
        )

        # Check the default_search value is set to "ytsearch2"
        self.assertEqual(
            ytdl_options.get("default_search"),
            "ytsearch2",
            _color_error_message_in_red(
                f'The "default_search" value of "ytdl_options" should have been set to "ytsearch2" ' +
                f'instead of "{ytdl_options.get("default_search")}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_video_from_spotify_song_returns_single_result_when_no_entries(self) -> None:

        """
        Test that get_video_from_spotify_song() returns the direct response when entries are missing.
        """

        response = {"title": "Single Result", "duration": 210}

        mock_ytdl_instance = Mock()
        mock_ytdl_instance.extract_info.return_value = response

        # Force YoutubeDL() to return mock_ytdl_instance
        with patch("Utils.Youtube.YoutubeDL") as mock_youtubedl:
            mock_youtubedl.return_value.__enter__.return_value = mock_ytdl_instance
            result = Utils.Youtube.get_video_from_spotify_song(
                Music_Manager = self._music_manager,
                song_title    = "Title",
                song_authors  = "Author"
            )

        # Check the result is not None if a single result is found in the Youtube search
        self.assertIsNotNone(
            result,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should not return None if a single result is found ' +
                f'in the Youtube search.'
            )
        )

        # Check it returned the shortest result (name and duration)
        title = "Single Result"
        self.assertEqual(
            result.get("title"),
            title,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should have returned the song name of the only ' +
                f'available result "{title}" instead of "{result.get("title")}".'
            )
        )
        self.assertEqual(
            result.get("duration"),
            210,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should have returned the song duration of the only ' +
                f'available result "210" instead of "{result.get("title")}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_video_from_spotify_song_returns_none_for_empty_response(self) -> None:

        """
        Test that get_video_from_spotify_song() returns None when extractor response is empty.
        """

        mock_ytdl_instance = Mock()
        mock_ytdl_instance.extract_info.return_value = {}

        # Force YoutubeDL() to return mock_ytdl_instance
        with patch("Utils.Youtube.YoutubeDL") as mock_youtubedl:
            mock_youtubedl.return_value.__enter__.return_value = mock_ytdl_instance
            result = Utils.Youtube.get_video_from_spotify_song(
                Music_Manager = self._music_manager,
                song_title    = "Title",
                song_authors  = "Author"
            )

        # Check None is returned when no results are found in the Youtube search
        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should have returned "None" ' +
                f'instead of "{result}" when no results are found in the Youtube search.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_video_from_spotify_song_returns_none_on_download_error(self) -> None:

        """
        Test that get_video_from_spotify_song() returns None when yt-dlp raises DownloadError.
        """

        error = "An error occurred when trying to donwload the video from Youtube"
        mock_ytdl_instance = Mock()
        mock_ytdl_instance.extract_info.side_effect = Utils.Youtube.DownloadError(error)

        # Force YoutubeDL() to raise a DownloadError
        with patch("Utils.Youtube.YoutubeDL") as mock_youtubedl:
            mock_youtubedl.return_value.__enter__.return_value = mock_ytdl_instance
            result = Utils.Youtube.get_video_from_spotify_song(
                Music_Manager = self._music_manager,
                song_title    = "Title",
                song_authors  = "Author"
            )

        # Check the result is None
        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should return "None" instead of "{result}" when ' +
                f'the download fails.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_video_from_spotify_song_returns_none_on_unexpected_error(self) -> None:

        """
        Test that get_video_from_spotify_song() returns None when an unexpected exception is raised.
        """

        error = "An error occurred when trying to donwload the video from Youtube"
        mock_ytdl_instance = Mock()
        mock_ytdl_instance.extract_info.side_effect = Exception(error)

        # Force YoutubeDL() to raise a DownloadError
        with patch("Utils.Youtube.YoutubeDL") as mock_youtubedl:
            mock_youtubedl.return_value.__enter__.return_value = mock_ytdl_instance
            result = Utils.Youtube.get_video_from_spotify_song(self._music_manager, "Song", "Author")

        # Check the result is None
        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "get_video_from_spotify_song()" function should return "None" instead of "{result}" when ' +
                f'an unexpected error occurs.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)