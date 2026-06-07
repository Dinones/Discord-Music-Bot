###########################################################################################################################
#   Tests for is_spotify_url() in Utils/Spotify.                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Spotify
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Is_Spotify_Url(unittest.TestCase):

    def test_returns_true_for_valid_https_spotify_urls(self) -> None:

        """
        Test that is_spotify_url() returns True for valid Spotify HTTPS URLs.
        """

        for link in (
            "https://open.spotify.com/track/abcdefghijklmnopqrstuv",
            "https://open.spotify.com/album/abcdefghijklmnopqrstuv",
            "https://open.spotify.com/playlist/abcdefghijklmnopqrstuv",
            "https://open.spotify.com/intl-es/track/abcdefghijklmnopqrstuv",
        ):
            result = Utils.Spotify.is_spotify_url(link)

            self.assertTrue(
                result,
                _color_error_message_in_red(
                    f'is_spotify_url() should return True for a valid Spotify URL "{link}".'
                )
            )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_false_for_http_url(self) -> None:

        """
        Test that is_spotify_url() returns False when the scheme is http instead of https.
        """

        result = Utils.Spotify.is_spotify_url("http://open.spotify.com/track/abcdefghijklmnopqrstuv")

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'is_spotify_url() should return False for an HTTP (non-HTTPS) Spotify URL.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_false_for_non_spotify_host(self) -> None:

        """
        Test that is_spotify_url() returns False when the host is not open.spotify.com.
        """

        for link in (
            "https://www.example.com/track/abcdefghijklmnopqrstuv",
            "https://api.spotify.com/v1/tracks/abcdefghijklmnopqrstuv",
            "https://spotify.com/track/abcdefghijklmnopqrstuv",
        ):
            result = Utils.Spotify.is_spotify_url(link)

            self.assertFalse(
                result,
                _color_error_message_in_red(
                    f'is_spotify_url() should return False for a non-Spotify host URL "{link}".'
                )
            )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_false_for_plain_text(self) -> None:

        """
        Test that is_spotify_url() returns False for plain text input.
        """

        result = Utils.Spotify.is_spotify_url("not a url at all")

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'is_spotify_url() should return False for plain text input.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_false_for_empty_string(self) -> None:

        """
        Test that is_spotify_url() returns False for an empty string.
        """

        result = Utils.Spotify.is_spotify_url("")

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'is_spotify_url() should return False for an empty string.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_false_for_whitespace_only(self) -> None:

        """
        Test that is_spotify_url() returns False for a whitespace-only string.
        """

        result = Utils.Spotify.is_spotify_url("   ")

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'is_spotify_url() should return False for a whitespace-only string.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
