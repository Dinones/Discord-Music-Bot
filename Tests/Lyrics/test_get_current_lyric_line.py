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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Lyrics import get_current_lyric_line
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_SAMPLE_LYRICS = [
    (10.0, "First line"),
    (20.0, "Second line"),
    (30.0, "Third line"),
]

###########################################################################################################################
###########################################################################################################################

class Test_Get_Current_Lyric_Line(unittest.TestCase):

    def test_empty_lyrics_returns_empty_string(self) -> None:

        result = get_current_lyric_line([], elapsed = 5.0)

        self.assertEqual(
            result,
            "",
            _color_error_message_in_red("Empty lyrics list should return empty string")
        )

    ###################################################################################################################

    def test_elapsed_before_first_timestamp_returns_empty_string(self) -> None:

        result = get_current_lyric_line(_SAMPLE_LYRICS, elapsed = 5.0)

        self.assertEqual(
            result,
            "",
            _color_error_message_in_red("Elapsed before first timestamp should return empty string")
        )

    ###################################################################################################################

    def test_elapsed_exactly_at_first_timestamp(self) -> None:

        result = get_current_lyric_line(_SAMPLE_LYRICS, elapsed = 10.0)

        self.assertEqual(
            result,
            "First line",
            _color_error_message_in_red("Elapsed at first timestamp should return first line")
        )

    ###################################################################################################################

    def test_elapsed_between_timestamps_returns_earlier_line(self) -> None:

        result = get_current_lyric_line(_SAMPLE_LYRICS, elapsed = 15.0)

        self.assertEqual(
            result,
            "First line",
            _color_error_message_in_red("Elapsed between timestamps should return the most recent line")
        )

    ###################################################################################################################

    def test_elapsed_exactly_at_second_timestamp(self) -> None:

        result = get_current_lyric_line(_SAMPLE_LYRICS, elapsed = 20.0)

        self.assertEqual(
            result,
            "Second line",
            _color_error_message_in_red("Elapsed at second timestamp should return second line")
        )

    ###################################################################################################################

    def test_elapsed_after_last_timestamp_returns_last_line(self) -> None:

        result = get_current_lyric_line(_SAMPLE_LYRICS, elapsed = 999.0)

        self.assertEqual(
            result,
            "Third line",
            _color_error_message_in_red("Elapsed after last timestamp should return last line")
        )

    ###################################################################################################################

    def test_elapsed_zero_with_lyrics_starting_at_zero(self) -> None:

        lyrics_at_zero = [(0.0, "Intro line"), (5.0, "Next line")]
        result = get_current_lyric_line(lyrics_at_zero, elapsed = 0.0)

        self.assertEqual(
            result,
            "Intro line",
            _color_error_message_in_red("Elapsed=0 with a line at timestamp 0 should return that line")
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main()
