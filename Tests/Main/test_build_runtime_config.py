###########################################################################################################################
#   Tests for _build_runtime_config() in Main.                                                                           #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest

import discord

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Main
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Build_Runtime_Config(unittest.TestCase):

    def test_returns_correct_env_field(self) -> None:

        """
        Test that _build_runtime_config() sets the env field from the provided env argument.
        """

        result = Main._build_runtime_config({}, "dev")

        self.assertEqual(
            result.env,
            "dev",
            _color_error_message_in_red(
                '_build_runtime_config() should set env to "dev" when env="dev" is passed.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_discord_server_name_from_secrets(self) -> None:

        """
        Test that _build_runtime_config() reads discord_server_name from secrets.
        """

        secrets = {"DISCORD_SERVER_NAME": "My Server"}

        result = Main._build_runtime_config(secrets, "dev")

        self.assertEqual(
            result.discord_server_name,
            "My Server",
            _color_error_message_in_red(
                '_build_runtime_config() should set discord_server_name from the DISCORD_SERVER_NAME secret.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_builds_activity_when_activity_name_is_present(self) -> None:

        """
        Test that _build_runtime_config() builds a discord.Activity when BOT_ACTIVITY_NAME is set.
        """

        secrets = {"BOT_ACTIVITY_NAME": "some music"}

        result = Main._build_runtime_config(secrets, "dev")

        self.assertIsNotNone(
            result.activity,
            _color_error_message_in_red(
                '_build_runtime_config() should build a discord.Activity when BOT_ACTIVITY_NAME is set.'
            )
        )
        self.assertIsInstance(
            result.activity,
            discord.Activity,
            _color_error_message_in_red(
                '_build_runtime_config() should return a discord.Activity instance.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_activity_is_none_when_activity_name_is_missing(self) -> None:

        """
        Test that _build_runtime_config() sets activity to None when BOT_ACTIVITY_NAME is absent.
        """

        result = Main._build_runtime_config({}, "dev")

        self.assertIsNone(
            result.activity,
            _color_error_message_in_red(
                '_build_runtime_config() should set activity to None when BOT_ACTIVITY_NAME is missing.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_parses_dev_channel_as_int(self) -> None:

        """
        Test that _build_runtime_config() parses DISCORD_TEXT_CHANNEL_DEV as an integer for env='dev'.
        """

        secrets = {"DISCORD_TEXT_CHANNEL_DEV": "123456789"}

        result = Main._build_runtime_config(secrets, "dev")

        self.assertEqual(
            result.discord_text_channel,
            123456789,
            _color_error_message_in_red(
                '_build_runtime_config() should parse DISCORD_TEXT_CHANNEL_DEV as int for env="dev".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_parses_prod_channel_for_prod_environment(self) -> None:

        """
        Test that _build_runtime_config() reads DISCORD_TEXT_CHANNEL_PROD when env='prod'.
        """

        secrets = {
            "DISCORD_TEXT_CHANNEL_PROD": "987654321",
            "DISCORD_TEXT_CHANNEL_DEV" : "111111111"
        }

        result = Main._build_runtime_config(secrets, "prod")

        self.assertEqual(
            result.discord_text_channel,
            987654321,
            _color_error_message_in_red(
                '_build_runtime_config() should read DISCORD_TEXT_CHANNEL_PROD for env="prod".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_discord_text_channel_is_none_for_non_digit_value(self) -> None:

        """
        Test that _build_runtime_config() sets discord_text_channel to None when the channel value is not a digit string.
        """

        secrets = {"DISCORD_TEXT_CHANNEL_DEV": "not-a-number"}

        result = Main._build_runtime_config(secrets, "dev")

        self.assertIsNone(
            result.discord_text_channel,
            _color_error_message_in_red(
                '_build_runtime_config() should set discord_text_channel to None when the value is not numeric.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_discord_text_channel_is_none_when_key_is_missing(self) -> None:

        """
        Test that _build_runtime_config() sets discord_text_channel to None when the key is absent from secrets.
        """

        result = Main._build_runtime_config({}, "dev")

        self.assertIsNone(
            result.discord_text_channel,
            _color_error_message_in_red(
                '_build_runtime_config() should set discord_text_channel to None when the key is missing.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
