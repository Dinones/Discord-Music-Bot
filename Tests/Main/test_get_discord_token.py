###########################################################################################################################
#   Tests for _get_discord_token() in Main.                                                                              #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Main
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Get_Discord_Token(unittest.TestCase):

    def test_returns_dev_token_for_dev_environment(self) -> None:

        """
        Test that _get_discord_token() returns the dev token when env is 'dev'.
        """

        secrets = {"DISCORD_MUSIC_BOT_TOKEN_DEV": "dev-token-abc"}

        result = Main._get_discord_token(secrets, "dev")

        self.assertEqual(
            result,
            "dev-token-abc",
            _color_error_message_in_red(
                '_get_discord_token() should return the DISCORD_MUSIC_BOT_TOKEN_DEV value for env="dev".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_prod_token_for_prod_environment(self) -> None:

        """
        Test that _get_discord_token() returns the prod token when env is 'prod'.
        """

        secrets = {"DISCORD_MUSIC_BOT_TOKEN_PROD": "prod-token-xyz"}

        result = Main._get_discord_token(secrets, "prod")

        self.assertEqual(
            result,
            "prod-token-xyz",
            _color_error_message_in_red(
                '_get_discord_token() should return the DISCORD_MUSIC_BOT_TOKEN_PROD value for env="prod".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_empty_string_when_key_is_missing(self) -> None:

        """
        Test that _get_discord_token() returns an empty string when the token key is absent from secrets.
        """

        result = Main._get_discord_token({}, "dev")

        self.assertEqual(
            result,
            "",
            _color_error_message_in_red(
                '_get_discord_token() should return "" when the token key is missing from secrets.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_strips_whitespace_from_token(self) -> None:

        """
        Test that _get_discord_token() strips surrounding whitespace from the token value.
        """

        secrets = {"DISCORD_MUSIC_BOT_TOKEN_DEV": "  my-token  "}

        result = Main._get_discord_token(secrets, "dev")

        self.assertEqual(
            result,
            "my-token",
            _color_error_message_in_red(
                '_get_discord_token() should strip whitespace from the token value.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_does_not_leak_prod_token_into_dev_env(self) -> None:

        """
        Test that _get_discord_token() does not return the prod token when env is 'dev'.
        """

        secrets = {
            "DISCORD_MUSIC_BOT_TOKEN_PROD": "prod-token-xyz",
            "DISCORD_MUSIC_BOT_TOKEN_DEV" : ""
        }

        result = Main._get_discord_token(secrets, "dev")

        self.assertEqual(
            result,
            "",
            _color_error_message_in_red(
                '_get_discord_token() must not return the prod token when env="dev".'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
