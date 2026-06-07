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
from typing import List, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Lyrics import calculate_lyric_sync_offset
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Calculate_Lyric_Sync_Offset(unittest.TestCase):

    def test_empty_lrc_returns_zero(self) -> None:

        result = calculate_lyric_sync_offset([], [(5.0, "Hello World here")])

        self.assertEqual(
            result,
            0.0,
            _color_error_message_in_red("Empty LRC list should return 0.0")
        )

    ###################################################################################################################

    def test_empty_vtt_returns_zero(self) -> None:

        result = calculate_lyric_sync_offset([(5.0, "Hello World here")], [])

        self.assertEqual(
            result,
            0.0,
            _color_error_message_in_red("Empty VTT list should return 0.0")
        )

    ###################################################################################################################

    def test_exact_match_returns_correct_offset(self) -> None:

        lrc = [(10.0, "is this the real life")]
        vtt = [(15.0, "is this the real life")]

        result = calculate_lyric_sync_offset(lrc, vtt)

        self.assertAlmostEqual(
            result,
            5.0,
            places = 1,
            msg = _color_error_message_in_red("Exact match at +5s offset should return 5.0")
        )

    ###################################################################################################################

    def test_negative_offset_returned_correctly(self) -> None:

        lrc = [(15.0, "is this the real life")]
        vtt = [(10.0, "is this the real life")]

        result = calculate_lyric_sync_offset(lrc, vtt)

        self.assertAlmostEqual(
            result,
            -5.0,
            places = 1,
            msg = _color_error_message_in_red("Match where VTT precedes LRC should return negative offset")
        )

    ###################################################################################################################

    def test_no_match_above_threshold_returns_zero(self) -> None:

        lrc = [(10.0, "aaaa bbbb cccc dddd")]
        vtt = [(15.0, "xxxx yyyy zzzz wwww")]

        result = calculate_lyric_sync_offset(lrc, vtt)

        self.assertEqual(
            result,
            0.0,
            _color_error_message_in_red("No match above similarity threshold should return 0.0")
        )

    ###################################################################################################################

    def test_implausible_offset_discarded(self) -> None:

        # Offset = 80 - 10 = 70 s, which exceeds _SYNC_MAX_OFFSET (60 s)
        lrc = [(10.0, "is this the real life")]
        vtt = [(80.0, "is this the real life")]

        result = calculate_lyric_sync_offset(lrc, vtt)

        self.assertEqual(
            result,
            0.0,
            _color_error_message_in_red("Offset exceeding 60s should be discarded and 0.0 returned")
        )

    ###################################################################################################################

    def test_single_word_line_skipped(self) -> None:

        # "Hello" is one word — below _SYNC_MIN_WORDS (2), so no offset is computed
        lrc = [(10.0, "Hello")]
        vtt = [(15.0, "Hello")]

        result = calculate_lyric_sync_offset(lrc, vtt)

        self.assertEqual(
            result,
            0.0,
            _color_error_message_in_red("Single-word lyric line should be skipped to avoid false-positive matches")
        )

    ###################################################################################################################

    def test_median_offset_selected_from_multiple_matches(self) -> None:

        # Three pairs with offsets [3, 5, 7] — median = 5
        lrc = [
            (10.0, "is this the real life"),
            (20.0, "is this just fantasy"),
            (30.0, "caught in a landslide"),
        ]
        vtt = [
            (13.0, "is this the real life"),
            (25.0, "is this just fantasy"),
            (37.0, "caught in a landslide"),
        ]

        result = calculate_lyric_sync_offset(lrc, vtt)

        self.assertAlmostEqual(
            result,
            5.0,
            places = 1,
            msg = _color_error_message_in_red("Median of offsets [3, 5, 7] should be 5.0")
        )

    ###################################################################################################################

    def test_accent_insensitive_matching(self) -> None:

        # "bébe lean" (accented) vs "bebe lean" (no accent) should still match
        lrc = [(10.0, "bébe lean aqui")]
        vtt = [(15.0, "bebe lean aqui")]

        result = calculate_lyric_sync_offset(lrc, vtt)

        self.assertAlmostEqual(
            result,
            5.0,
            places = 1,
            msg = _color_error_message_in_red("Accented LRC text should match unaccented VTT text after normalization")
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main()
