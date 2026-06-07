###########################################################################################################################
#   Tests for parse_spotify_link() in Utils/Spotify.                                                                     #
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
import Utils.Constants as CONST
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Parse_Spotify_Link(unittest.TestCase):

    def test_parse_spotify_link_returns_link_type_and_id_for_supported_links(self) -> None:

        """
        Test that _parse_spotify_link() returns the link type and Spotify ID for supported links.
        """

        for spotify_link, expected_type in (
            (CONST.TESTING_SPOTIFY_SONG_LINK, "track"),
            (CONST.TESTING_SPOTIFY_ALBUM_LINK, "album"),
            (CONST.TESTING_SPOTIFY_PLAYLIST_LINK, "playlist"),
            ("https://open.spotify.com/intl-es/track/abcdefghijklmnopqrstuv", "track")
        ):
            result = Utils.Spotify._parse_spotify_link(spotify_link)

            expected_id = spotify_link.rstrip("/").split("/")[-1]
            self.assertEqual(
                result,
                (expected_type, expected_id),
                _color_error_message_in_red(
                    f'The "_parse_spotify_link()" function should have returned the "{expected_type}" type and ' +
                    f'"{expected_id}" Spotify ID for "{spotify_link}" instead of "{result}".'
                )
            )

    #######################################################################################################################
    #######################################################################################################################

    def test_parse_spotify_link_returns_none_for_invalid_links(self) -> None:

        """
        Test that _parse_spotify_link() returns None for invalid links.
        """

        for spotify_link in (
            "",
            "track/abcdefghijklmnopqrstuv",
            "https://open.spotify.com/track/short-id"
            "https://example.com/track/abcdefghijklmnopqrstuv",
            "ftp://open.spotify.com/track/abcdefghijklmnopqrstuv",
            "https://open.spotify.com/show/abcdefghijklmnopqrstuv",
        ):
            result = Utils.Spotify._parse_spotify_link(spotify_link)

            self.assertIsNone(
                result,
                _color_error_message_in_red(
                    f'The invalid Spotify link "{spotify_link}" should have returned "None" instead of "{result}".'
                )
            )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
