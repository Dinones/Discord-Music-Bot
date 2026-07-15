###########################################################################################################################
#   Tests for _get_secrets_from_env() in Utils/AWS_Secrets.                                                              #
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

import Utils.AWS_Secrets as AWS_Secrets
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Get_Secrets_From_Env(unittest.TestCase):

    def test_returns_empty_dict_when_no_env_vars_set(self) -> None:

        """
        Test that _get_secrets_from_env() returns an empty dict when none of the expected keys are set.
        """

        with patch.dict(os.environ, {}, clear = True):
            result = AWS_Secrets._get_secrets_from_env()

        self.assertEqual(
            result,
            {},
            _color_error_message_in_red(
                f'The "_get_secrets_from_env()" function should return "{{}}" instead of "{result}" ' +
                'when no environment variables are set.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_reads_expected_string_keys_from_environment(self) -> None:

        """
        Test that _get_secrets_from_env() picks up every expected string key present in the environment.
        """

        fake_env = {
            "DISCORD_MUSIC_BOT_TOKEN_DEV" : "dev-token",
            "SPOTIFY_CLIENT_ID"           : "client-id",
            "SPOTIFY_CLIENT_SECRET"       : "client-secret",
        }

        with patch.dict(os.environ, fake_env, clear = True):
            result = AWS_Secrets._get_secrets_from_env()

        self.assertEqual(
            result,
            fake_env,
            _color_error_message_in_red(
                f'The "_get_secrets_from_env()" function should return "{fake_env}" instead of "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_skips_blank_string_keys(self) -> None:

        """
        Test that _get_secrets_from_env() ignores environment variables that are set but blank.
        """

        with patch.dict(os.environ, {"SPOTIFY_CLIENT_ID": "  "}, clear = True):
            result = AWS_Secrets._get_secrets_from_env()

        self.assertNotIn(
            "SPOTIFY_CLIENT_ID",
            result,
            _color_error_message_in_red(
                'The "_get_secrets_from_env()" function should not include blank environment variables.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_parses_spotify_playlists_json_array(self) -> None:

        """
        Test that _get_secrets_from_env() parses SPOTIFY_PLAYLISTS as a JSON array when present.
        """

        fake_playlists = [{"name": "Party", "url": "https://open.spotify.com/playlist/abc"}]

        with patch.dict(os.environ, {"SPOTIFY_PLAYLISTS": '[{"name": "Party", "url": "https://open.spotify.com/playlist/abc"}]'}, clear = True):
            result = AWS_Secrets._get_secrets_from_env()

        self.assertEqual(
            result.get("SPOTIFY_PLAYLISTS"),
            fake_playlists,
            _color_error_message_in_red(
                f'The "_get_secrets_from_env()" function should parse "SPOTIFY_PLAYLISTS" into "{fake_playlists}" ' +
                f'instead of "{result.get("SPOTIFY_PLAYLISTS")}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_ignores_invalid_spotify_playlists_json(self) -> None:

        """
        Test that _get_secrets_from_env() omits SPOTIFY_PLAYLISTS and logs instead of raising on invalid JSON.
        """

        with (
            patch.dict(os.environ, {"SPOTIFY_PLAYLISTS": "not json"}, clear = True),
            patch("Utils.AWS_Secrets.print") as mock_print,
            patch("Utils.AWS_Secrets.save_exception_to_txt") as mock_save_exception
        ):
            result = AWS_Secrets._get_secrets_from_env()

        self.assertNotIn(
            "SPOTIFY_PLAYLISTS",
            result,
            _color_error_message_in_red(
                'The "_get_secrets_from_env()" function should not include "SPOTIFY_PLAYLISTS" when its JSON is invalid.'
            )
        )

        self.assertEqual(
            mock_print.call_count,
            1,
            _color_error_message_in_red(
                'Exactly "1" logging message should have been printed when "SPOTIFY_PLAYLISTS" JSON is invalid ' +
                f'instead of "{mock_print.call_count}".'
            )
        )

        expected_title = "Parse_Env_Playlists"
        self.assertEqual(
            mock_save_exception.call_args.kwargs.get("title"),
            expected_title,
            _color_error_message_in_red(
                f'The "save_exception_to_txt()" function should have been called with the "{expected_title}" argument ' +
                f'instead of "{mock_save_exception.call_args.kwargs.get("title")}".'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
