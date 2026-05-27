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
from typing import Dict, Any
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Spotify
import Utils.Constants as CONST
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Craft_Spotify_Token(unittest.TestCase):

    def setUp(self) -> None:

        Utils.Spotify.SPOTIFY_AUTH_CACHE.clear()

    #######################################################################################################################
    #######################################################################################################################

    def _build_response(self, payload: Dict[str, Any]) -> Mock:

        response = Mock()
        response.json.return_value = payload

        return response

    #######################################################################################################################
    #######################################################################################################################

    def test_craft_spotify_token_reuses_cached_token_before_expiration(self) -> None:

        """
        Test that __craft_spotify_token() reuses the in-memory token while it is still valid.
        """

        Utils.Spotify.SPOTIFY_AUTH_CACHE.update(
            {
                "SPOTIFY_CLIENT_ID"        : "client-id",
                "SPOTIFY_CLIENT_SECRET"    : "client-secret",
                "SPOTIFY_ACCESS_TOKEN"     : "cached-token",
                "SPOTIFY_TOKEN_EXPIRES_AT" : 5000
            }
        )

        with (
            patch("Utils.Spotify.time", return_value = 1000),
            patch("Utils.Spotify.requests.post") as mock_post
        ):
            result = Utils.Spotify.__dict__["__craft_spotify_token"]()

        cached_token_name = Utils.Spotify.SPOTIFY_AUTH_CACHE.get('SPOTIFY_ACCESS_TOKEN')
        self.assertEqual(
            result,
            cached_token_name,
            _color_error_message_in_red(
                f'The __craft_spotify_token() function should have been reused the cached token "{cached_token_name}"' +
                f' instead of "{result}".'
            )
        )

        self.assertFalse(
            mock_post.called,
            _color_error_message_in_red(
                'Spotify should not have requested a new token while the cache is still valid.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_craft_spotify_token_refreshes_expired_token_and_updates_cache(self) -> None:

        """
        Test that __craft_spotify_token() refreshes the token when the cached one is expired.
        """

        Utils.Spotify.SPOTIFY_AUTH_CACHE.update(
            {
                "SPOTIFY_CLIENT_ID"        : "client-id",
                "SPOTIFY_CLIENT_SECRET"    : "client-secret",
                "SPOTIFY_ACCESS_TOKEN"     : "expired-token",
                "SPOTIFY_TOKEN_EXPIRES_AT" : 1000
            }
        )

        response = self._build_response(
            {
                "access_token" : "new-token",
                "expires_in"   : 3600
            }
        )

        with (
            patch("Utils.Spotify.time", return_value = 5000),
            patch("Utils.Spotify.requests.post", return_value = response) as mock_post
        ):
            result = Utils.Spotify.__dict__["__craft_spotify_token"]()

        new_token = "new-token"
        self.assertEqual(
            result,
            new_token,
            _color_error_message_in_red(
                f'The expired Spotify token "{result}" should have been refreshed with "{new_token}".'
            )
        )

        old_token = Utils.Spotify.SPOTIFY_AUTH_CACHE.get("SPOTIFY_ACCESS_TOKEN")
        self.assertEqual(
            old_token,
            new_token,
            _color_error_message_in_red(
                f'The expired Spotify token "{old_token}" should have been replaced in-memory with the new one ' + 
                f'"{new_token}".'
            )
        )

        new_expiration_date = Utils.Spotify.SPOTIFY_AUTH_CACHE.get("SPOTIFY_TOKEN_EXPIRES_AT")
        expected_expiration_date = 5000 + (3600 - CONST.SPOTIFY_TOKEN_EXPIRATION_BUFFER_SECONDS)
        self.assertEqual(
            new_expiration_date,
            expected_expiration_date,
            _color_error_message_in_red(
                f'The Spotify token expiration date should be "{expected_expiration_date}" instead of ' +
                f'{new_expiration_date}.'
            )
        )

        self.assertEqual(
            mock_post.call_count,
            1,
            _color_error_message_in_red(
                f'The "requests.post()" function should have been called exactly "1" time instead of ' +
                f'"{mock_post.call_count}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_craft_spotify_token_returns_empty_string_when_spotify_returns_no_access_token(self) -> None:

        """
        Test that __craft_spotify_token() returns an empty string when Spotify omits the access token.
        """

        Utils.Spotify.SPOTIFY_AUTH_CACHE.update(
            {
                "SPOTIFY_CLIENT_ID"     : "client-id",
                "SPOTIFY_CLIENT_SECRET" : "client-secret"
            }
        )

        response = self._build_response({"expires_in": 3600})

        with patch("Utils.Spotify.requests.post", return_value = response):
            result = Utils.Spotify.__dict__["__craft_spotify_token"]()

        self.assertEqual(
            result,
            "",
            _color_error_message_in_red(
                f'The "__craft_spotify_token()" function should have returned an empty string "" instead of "{result}" ' +
                f'if the Spotify response does not provide a valid token.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
