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

from Utils.Lyrics import parse_lrc
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Parse_Lrc(unittest.TestCase):

    def test_empty_string_returns_empty_list(self) -> None:

        result = parse_lrc("")

        self.assertEqual(
            result,
            [],
            _color_error_message_in_red("Empty LRC string should return []")
        )

    ###################################################################################################################

    def test_non_timestamp_lines_are_skipped(self) -> None:

        lrc = "[ti:Bohemian Rhapsody]\n[ar:Queen]\nsome plain text"
        result = parse_lrc(lrc)

        self.assertEqual(
            result,
            [],
            _color_error_message_in_red("Header/plain lines without valid timestamps should be skipped")
        )

    ###################################################################################################################

    def test_single_line_no_fraction(self) -> None:

        result = parse_lrc("[01:23]Hello world")

        self.assertEqual(
            len(result),
            1,
            _color_error_message_in_red("Should parse one line")
        )
        self.assertAlmostEqual(
            result[0][0],
            83.0,
            places = 3,
            msg = _color_error_message_in_red("1:23 should equal 83.0 seconds")
        )
        self.assertEqual(
            result[0][1],
            "Hello world",
            _color_error_message_in_red("Text should be stripped and returned correctly")
        )

    ###################################################################################################################

    def test_fractional_seconds_two_digits(self) -> None:

        result = parse_lrc("[00:05.25]Test line")

        self.assertAlmostEqual(
            result[0][0],
            5.250,
            places = 3,
            msg = _color_error_message_in_red("[00:05.25] should equal 5.250 seconds")
        )

    ###################################################################################################################

    def test_fractional_seconds_three_digits(self) -> None:

        result = parse_lrc("[00:10.123]Another line")

        self.assertAlmostEqual(
            result[0][0],
            10.123,
            places = 3,
            msg = _color_error_message_in_red("[00:10.123] should equal 10.123 seconds")
        )

    ###################################################################################################################

    def test_fractional_seconds_one_digit_padded(self) -> None:

        # [00:05.5] → fraction "5" padded to "500" ms → 0.500 s
        result = parse_lrc("[00:05.5]Line")

        self.assertAlmostEqual(
            result[0][0],
            5.500,
            places = 3,
            msg = _color_error_message_in_red("[00:05.5] should equal 5.500 seconds (padded to ms)")
        )

    ###################################################################################################################

    def test_multiple_lines_sorted_by_timestamp(self) -> None:

        lrc = "[00:30]Third\n[00:10]First\n[00:20]Second"
        result = parse_lrc(lrc)

        self.assertEqual(
            len(result),
            3,
            _color_error_message_in_red("Should parse 3 lines")
        )
        self.assertEqual(
            [text for _, text in result],
            ["First", "Second", "Third"],
            _color_error_message_in_red("Lines should be sorted ascending by timestamp")
        )

    ###################################################################################################################

    def test_mixed_valid_and_invalid_lines(self) -> None:

        lrc = "[00:01]Valid line\n[invalid]Bad line\n[00:02]Another valid"
        result = parse_lrc(lrc)

        self.assertEqual(
            len(result),
            2,
            _color_error_message_in_red("Only timestamp lines should be included")
        )

    ###################################################################################################################

    def test_whitespace_stripped_from_text(self) -> None:

        result = parse_lrc("[00:01]   spaces around   ")

        self.assertEqual(
            result[0][1],
            "spaces around",
            _color_error_message_in_red("Text should be stripped of leading/trailing whitespace")
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main()
