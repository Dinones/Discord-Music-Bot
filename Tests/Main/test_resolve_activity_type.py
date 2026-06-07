###########################################################################################################################
#   Tests for _resolve_activity_type() in Main.                                                                          #
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

class Test_Resolve_Activity_Type(unittest.TestCase):

    def test_known_activity_types_resolve_correctly(self) -> None:

        """
        Test that _resolve_activity_type() maps all supported string values to their discord.ActivityType counterparts.
        """

        cases = (
            ("playing",   discord.ActivityType.playing),
            ("watching",  discord.ActivityType.watching),
            ("streaming", discord.ActivityType.streaming),
            ("listening", discord.ActivityType.listening),
            ("competing", discord.ActivityType.competing),
        )

        for activity_str, expected_type in cases:
            result = Main._resolve_activity_type(activity_str)

            self.assertEqual(
                result,
                expected_type,
                _color_error_message_in_red(
                    f'_resolve_activity_type("{activity_str}") should return {expected_type}, got {result}.'
                )
            )

    #######################################################################################################################
    #######################################################################################################################

    def test_normalizes_uppercase_input(self) -> None:

        """
        Test that _resolve_activity_type() normalizes uppercase input before matching.
        """

        result = Main._resolve_activity_type("LISTENING")

        self.assertEqual(
            result,
            discord.ActivityType.listening,
            _color_error_message_in_red(
                '_resolve_activity_type("LISTENING") should return discord.ActivityType.listening.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_strips_whitespace_from_input(self) -> None:

        """
        Test that _resolve_activity_type() strips surrounding whitespace before matching.
        """

        result = Main._resolve_activity_type("  playing  ")

        self.assertEqual(
            result,
            discord.ActivityType.playing,
            _color_error_message_in_red(
                '_resolve_activity_type("  playing  ") should return discord.ActivityType.playing.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_defaults_to_listening_for_unknown_type(self) -> None:

        """
        Test that _resolve_activity_type() defaults to discord.ActivityType.listening for unknown values.
        """

        result = Main._resolve_activity_type("dancing")

        self.assertEqual(
            result,
            discord.ActivityType.listening,
            _color_error_message_in_red(
                '_resolve_activity_type("dancing") should default to discord.ActivityType.listening.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
