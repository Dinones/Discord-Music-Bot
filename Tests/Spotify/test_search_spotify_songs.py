###########################################################################################################################
#   Tests for search_spotify_songs() in Utils/Spotify.                                                                   #
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

import Utils.Spotify
import Utils.Constants as CONST
from Tests.Helpers.helpers import _build_test_message, _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Search_Spotify_Songs(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.message = _build_test_message()
        self._to_thread = AsyncMock(side_effect = lambda function, *args: function(*args))

    #######################################################################################################################
    #######################################################################################################################

    async def test_search_spotify_songs_returns_empty_list_for_invalid_link(self) -> None:

        """
        Test that search_spotify_songs() returns an empty list when the Spotify link is invalid.
        """

        with (
            patch("Utils.Spotify.asyncio.to_thread", new = self._to_thread),
            patch("Utils.Spotify.__craft_spotify_token") as mock_craft_token
        ):
            result = await Utils.Spotify.search_spotify_songs(
                message      = self.message,
                spotify_link = "https://example.com/not-spotify"
            )

        self.assertEqual(
            result,
            [],
            _color_error_message_in_red(
                f'The "search_spotify_songs()" function should have returned an empty list "[]" for an invalid link ' +
                f'instead of "{result}".'
            )
        )

        self.assertFalse(
            mock_craft_token.called,
            _color_error_message_in_red(
                f'The "__craft_spotify_token()" function should not have been requested for an invalid link.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_search_spotify_songs_returns_empty_list_when_token_cannot_be_retrieved(self) -> None:

        """
        Test that search_spotify_songs() returns an empty list when Spotify token creation fails.
        """

        with (
            patch("Utils.Spotify.asyncio.to_thread", new = self._to_thread),
            patch("Utils.Spotify.__craft_spotify_token", return_value = "")
        ):
            result = await Utils.Spotify.search_spotify_songs(
                message      = self.message,
                spotify_link = CONST.TESTING_SPOTIFY_SONG_LINK
            )

        self.assertEqual(
            result,
            [],
            _color_error_message_in_red(
                f'The "search_spotify_songs()" function should have returned an empty list "[]" instead of {result} ' +
                f'when token creation fails.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_search_spotify_songs_returns_track_payload_for_valid_track_link(self) -> None:

        """
        Test that search_spotify_songs() returns a one-element list when the Spotify link is a track.
        """

        payload = {"id": "abcdefghijklmnopqrstuv", "name": "Song"}

        with (
            patch("Utils.Spotify.asyncio.to_thread", new = self._to_thread),
            patch("Utils.Spotify.__craft_spotify_token", return_value = "spotify-token"),
            patch("Utils.Spotify._fetch_spotify_track", return_value = payload)
        ):
            result = await Utils.Spotify.search_spotify_songs(
                message      = self.message,
                spotify_link = CONST.TESTING_SPOTIFY_SONG_LINK
            )

        self.assertEqual(
            result,
            [payload],
            _color_error_message_in_red(
                f'The "search_spotify_songs()" function should have returned "[{payload}]" instead of "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_search_spotify_songs_returns_empty_list_and_logs_on_fetch_error(self) -> None:

        """
        Test that search_spotify_songs() returns an empty list and saves a log when fetching raises.
        """

        with (
            patch("Utils.Spotify.asyncio.to_thread", new = self._to_thread),
            patch("Utils.Spotify.__craft_spotify_token", return_value = "spotify-token"),
            patch("Utils.Spotify._fetch_spotify_track", side_effect = Exception("fetch error")),
            patch("Utils.Spotify.save_exception_to_txt") as mock_save_exception
        ):
            result = await Utils.Spotify.search_spotify_songs(
                message      = self.message,
                spotify_link = CONST.TESTING_SPOTIFY_SONG_LINK
            )

        self.assertEqual(
            result,
            [],
            _color_error_message_in_red(
                'search_spotify_songs() should return an empty list when the fetch raises an exception.'
            )
        )

        self.assertEqual(
            mock_save_exception.call_count,
            1,
            _color_error_message_in_red(
                'search_spotify_songs() should call save_exception_to_txt() exactly once on fetch error.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
