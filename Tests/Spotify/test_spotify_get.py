###########################################################################################################################
#   Tests for _spotify_get() in Utils/Spotify.                                                                           #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
import requests
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Constants as CONST
import Utils.Spotify
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Spotify_Get(unittest.TestCase):

    def _build_response(self, payload, status_code: int = 200, text: str = "") -> Mock:

        response = Mock()
        response.status_code = status_code
        response.text = text
        response.json.return_value = payload

        return response

    #######################################################################################################################
    #######################################################################################################################

    def test_get_spotify_response_returns_json_payload_on_success(self) -> None:

        """
        Test that _get_spotify_response() returns the decoded JSON payload on success.
        """

        payload = {"id": "123"}

        with patch("Utils.Spotify.requests.get", return_value = self._build_response(payload)) as mock_get:
            result = Utils.Spotify._get_spotify_response(
                url     = "https://api.spotify.com/v1/tracks/123",
                headers = {"Authorization": "Bearer token"}
            )

        self.assertEqual(
            result,
            payload,
            _color_error_message_in_red(
                f'The "_get_spotify_response()" function should have returned "{payload}" instead of "{result}".'
            )
        )

        mock_get.assert_called_once_with(
            url     = "https://api.spotify.com/v1/tracks/123",
            headers = {"Authorization": "Bearer token"},
            params  = None,
            timeout = CONST.SPOTIFY_REQUEST_TIMEOUT
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_spotify_response_raises_exception_on_request_error(self) -> None:

        """
        Test that _get_spotify_response() raises when requests raises a RequestException.
        """

        with (
            patch("Utils.Spotify.requests.get", side_effect = requests.RequestException("network error")),
            patch("Utils.Spotify.save_exception_to_txt") as mock_save_exception
        ):
            with self.assertRaises(Exception):
                Utils.Spotify._get_spotify_response(
                    url     = "https://api.spotify.com/v1/tracks/123",
                    headers = {"Authorization": "Bearer token"}
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

    def test_get_spotify_response_raises_exception_on_invalid_status_code(self) -> None:

        """
        Test that _get_spotify_response() raises when Spotify returns an error status code.
        """

        with (
            patch("Utils.Spotify.requests.get", return_value = self._build_response({}, status_code = 500)),
            patch("Utils.Spotify.save_exception_to_txt") as mock_save_exception
        ):
            with self.assertRaises(Exception):
                Utils.Spotify._get_spotify_response(
                    url     = "https://api.spotify.com/v1/tracks/123",
                    headers = {"Authorization": "Bearer token"}
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

    def test_get_spotify_response_raises_exception_on_invalid_json_payload(self) -> None:

        """
        Test that _get_spotify_response() raises when Spotify returns an invalid JSON payload.
        """

        response = self._build_response({})
        response.json.side_effect = ValueError("invalid json")

        with (
            patch("Utils.Spotify.requests.get", return_value = response),
            patch("Utils.Spotify.save_exception_to_txt") as mock_save_exception
        ):
            with self.assertRaises(Exception):
                Utils.Spotify._get_spotify_response(
                    url     = "https://api.spotify.com/v1/tracks/123",
                    headers = {"Authorization": "Bearer token"}
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

    def test_get_spotify_response_raises_exception_when_payload_is_not_a_dictionary(self) -> None:

        """
        Test that _get_spotify_response() raises when Spotify returns a JSON payload that is not a dictionary.
        """

        with (
            patch("Utils.Spotify.requests.get", return_value = self._build_response(["not", "a", "dict"])),
            patch("Utils.Spotify.save_exception_to_txt") as mock_save_exception
        ):
            with self.assertRaises(Exception):
                Utils.Spotify._get_spotify_response(
                    url     = "https://api.spotify.com/v1/tracks/123",
                    headers = {"Authorization": "Bearer token"}
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
