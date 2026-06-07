###########################################################################################################################
#   Tests for get_spotify_secrets() in Utils/Spotify.                                                                    #
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

import Utils.Spotify
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Get_Spotify_Secrets(unittest.TestCase):

    def setUp(self) -> None:

        Utils.Spotify.SPOTIFY_AUTH_CACHE.clear()

    #######################################################################################################################
    #######################################################################################################################

    def test_get_spotify_secrets_returns_in_memory_cache_when_available(self) -> None:

        """
        Test that _get_spotify_secrets() returns cached Spotify secrets without calling AWS.
        """

        Utils.Spotify.SPOTIFY_AUTH_CACHE.update(
            {
                "SPOTIFY_CLIENT_ID"     : "client-id",
                "SPOTIFY_CLIENT_SECRET" : "client-secret"
            }
        )

        with patch("Utils.Spotify.get_secrets") as mock_get_secrets:
            result = Utils.Spotify._get_spotify_secrets()

        self.assertEqual(
            result,
            Utils.Spotify.SPOTIFY_AUTH_CACHE,
            _color_error_message_in_red(
                f'The "_get_spotify_secrets()" function should have returned the in-memory cache ' +
                f'"{Utils.Spotify.SPOTIFY_AUTH_CACHE}" instead of "{result}".'
            )
        )

        self.assertFalse(
            mock_get_secrets.called,
            _color_error_message_in_red(
                'The "_get_spotify_secrets()" function should have not called the get_secrets() function if the secrets ' +
                'were stored in-memory.')
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_spotify_secrets_retrieves_secrets_from_aws_and_stores_them_in_memory(self) -> None:

        """
        Test that _get_spotify_secrets() retrieves Spotify secrets from AWS and caches them.
        """

        spotify_secrets = {
            "SPOTIFY_CLIENT_ID"     : "client-id",
            "SPOTIFY_CLIENT_SECRET" : "client-secret"
        }

        with patch("Utils.Spotify.get_secrets", return_value = spotify_secrets):
            result = Utils.Spotify._get_spotify_secrets()

        self.assertEqual(
            result,
            spotify_secrets,
            _color_error_message_in_red(
                f'The "_get_spotify_secrets()" function should have returned "{spotify_secrets}" instead of "{result}".'
            )
        )

        self.assertEqual(
            Utils.Spotify.SPOTIFY_AUTH_CACHE,
            spotify_secrets,
            _color_error_message_in_red(
                f'The retrieved Spotify secrets "{spotify_secrets}" should have been stored in-memory ' +
                f'"{Utils.Spotify.SPOTIFY_AUTH_CACHE}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_spotify_secrets_returns_none_when_aws_payload_is_missing_required_keys(self) -> None:

        """
        Test that _get_spotify_secrets() returns None when AWS does not provide Spotify credentials.
        """

        with patch("Utils.Spotify.get_secrets", return_value = {"OTHER_SECRET": "value"}):
            result = Utils.Spotify._get_spotify_secrets()

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "_get_spotify_secrets()" function should have returned "None" instead of "{result}".'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
