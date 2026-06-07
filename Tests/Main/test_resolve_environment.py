###########################################################################################################################
#   Tests for _resolve_environment() in Main.                                                                            #
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

import Main
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Resolve_Environment(unittest.TestCase):

    def test_returns_prod_when_bot_env_is_prod(self) -> None:

        """
        Test that _resolve_environment() returns 'prod' when BOT_ENV=prod.
        """

        with patch.dict("os.environ", {"BOT_ENV": "prod"}):
            result = Main._resolve_environment()

        self.assertEqual(
            result,
            "prod",
            _color_error_message_in_red(
                '_resolve_environment() should return "prod" when BOT_ENV is set to "prod".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_dev_when_bot_env_is_dev(self) -> None:

        """
        Test that _resolve_environment() returns 'dev' when BOT_ENV=dev.
        """

        with patch.dict("os.environ", {"BOT_ENV": "dev"}):
            result = Main._resolve_environment()

        self.assertEqual(
            result,
            "dev",
            _color_error_message_in_red(
                '_resolve_environment() should return "dev" when BOT_ENV is set to "dev".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_defaults_to_dev_when_bot_env_is_not_set(self) -> None:

        """
        Test that _resolve_environment() defaults to 'dev' when BOT_ENV is absent.
        """

        with patch.dict("os.environ", {}, clear = False):
            os.environ.pop("BOT_ENV", None)
            result = Main._resolve_environment()

        self.assertEqual(
            result,
            "dev",
            _color_error_message_in_red(
                '_resolve_environment() should default to "dev" when BOT_ENV is not set.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_normalizes_uppercase_value(self) -> None:

        """
        Test that _resolve_environment() normalizes BOT_ENV to lowercase before matching.
        """

        with patch.dict("os.environ", {"BOT_ENV": "PROD"}):
            result = Main._resolve_environment()

        self.assertEqual(
            result,
            "prod",
            _color_error_message_in_red(
                '_resolve_environment() should normalize BOT_ENV to lowercase ("PROD" → "prod").'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_strips_whitespace_from_value(self) -> None:

        """
        Test that _resolve_environment() strips surrounding whitespace from BOT_ENV.
        """

        with patch.dict("os.environ", {"BOT_ENV": "  prod  "}):
            result = Main._resolve_environment()

        self.assertEqual(
            result,
            "prod",
            _color_error_message_in_red(
                '_resolve_environment() should strip whitespace from BOT_ENV ("  prod  " → "prod").'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_falls_back_to_dev_for_unknown_value(self) -> None:

        """
        Test that _resolve_environment() falls back to 'dev' for an unrecognised BOT_ENV value.
        """

        with patch.dict("os.environ", {"BOT_ENV": "staging"}):
            result = Main._resolve_environment()

        self.assertEqual(
            result,
            "dev",
            _color_error_message_in_red(
                '_resolve_environment() should fall back to "dev" for an unrecognised BOT_ENV value.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
