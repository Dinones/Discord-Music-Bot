###########################################################################################################################
#   Tests for _fetch_spotify_track() in Utils/Spotify.                                                                   #
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

class Test_Fetch_Spotify_Track(unittest.TestCase):

    def test_fetch_spotify_track_returns_track_payload(self) -> None:

        """
        Test that _fetch_spotify_track() returns the Spotify track payload.
        """

        payload = {
            "id"   : "song_id",
            "name" : "Song"
        }

        with patch("Utils.Spotify._get_spotify_response", return_value = payload) as mock_get_spotify_response:
            result = Utils.Spotify._fetch_spotify_track(
                spotify_id   = payload["id"],
                access_token = "spotify-token"
            )

        self.assertEqual(
            result,
            payload,
            _color_error_message_in_red(
                f'The "_fetch_spotify_track()" function should have returned "{payload}" instead of "{result}".'
            )
        )

        mock_get_spotify_response.assert_called_once_with(
            "https://api.spotify.com/v1/tracks/song_id",
            {"Authorization": "Bearer spotify-token"},
            {"market": CONST.SPOTIFY_DEFAULT_MARKET}
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_fetch_spotify_track_raises_exception_when_payload_has_no_id(self) -> None:

        """
        Test that _fetch_spotify_track() raises when the Spotify payload does not include an ID.
        """

        with (
            patch("Utils.Spotify._get_spotify_response", return_value = {"name": "Song"}),
            patch("Utils.Spotify.save_exception_to_txt") as mock_save_exception
        ):
            with self.assertRaises(Exception):
                Utils.Spotify._fetch_spotify_track(
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
