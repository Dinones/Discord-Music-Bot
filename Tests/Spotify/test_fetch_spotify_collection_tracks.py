
###########################################################################################################################
#   Tests for fetch_spotify_collection_tracks() in Utils/Spotify.                                                        #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Constants as CONST
import Utils.Spotify
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Fetch_Spotify_Collection_Tracks(unittest.TestCase):

    def test_fetch_spotify_collection_tracks_paginates_and_filters_playlist_tracks(self) -> None:

        """
        Test that _fetch_spotify_collection_tracks() paginates playlist tracks and skips removed entries.
        """

        first_page = {
            "items": [
                {"track": {"id": "song-1", "name": "First"}},
                {"track": None}
            ],
            "next": "https://api.spotify.com/v1/playlists/next-page"
        }

        second_page = {
            "items": [
                {"track": {"id": "song-2", "name": "Second"}},
                {"track": {"name": "Missing ID"}}
            ],
            "next": None
        }

        with patch("Utils.Spotify._get_spotify_response", side_effect = [first_page, second_page]) as mock_get_spotify_response:
            result = Utils.Spotify._fetch_spotify_collection_tracks(
                link_type    = "playlist",
                spotify_id   = "abcdefghijklmnopqrstuv",
                access_token = "spotify-token"
            )

        valid_tracks = ["First", "Second"]
        returned_tracks = [track.get("name") for track in result]
        self.assertEqual(
            returned_tracks,
            valid_tracks,
            _color_error_message_in_red(
                f'The "_fetch_spotify_collection_tracks()" function should have kept only valid the playlist tracks ' +
                f'{valid_tracks} instead of all of them {returned_tracks}.'
            )
        )

        self.assertEqual(
            mock_get_spotify_response.call_count,
            2,
            _color_error_message_in_red(
                f'The _get_spotify_response() function should have been called exactly "2" times instead of ' +
                f'"{mock_get_spotify_response.call_count}".'
            )
        )

        self.assertEqual(
            mock_get_spotify_response.call_args_list[0].args[2],
            {"limit": 50, "offset": 0, "market": CONST.SPOTIFY_DEFAULT_MARKET},
            _color_error_message_in_red(
                f'The first _get_spotify_response() call should include the default market and pagination controls.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_fetch_spotify_collection_tracks_raises_exception_when_items_is_not_a_list(self) -> None:

        """
        Test that _fetch_spotify_collection_tracks() raises when Spotify returns an invalid items payload.
        """

        with (
            patch("Utils.Spotify._get_spotify_response", return_value = {"items": {}, "next": None}),
            patch("Utils.Spotify.save_exception_to_txt") as mock_save_exception
        ):
            with self.assertRaises(Exception):
                Utils.Spotify._fetch_spotify_collection_tracks(
                    link_type    = "album",
                    spotify_id   = "abcdefghijklmnopqrstuv",
                    access_token = "spotify-token"
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
