###########################################################################################################################
#   Tests for the _format_time() helper in Now_Playing_Updater.                                                          #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Embed.Now_Playing_Updater import _format_time
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Format_Time(unittest.TestCase):

    def test_zero_seconds_formats_as_zero_colon_zero(self) -> None:

        """
        Test that _format_time() formats 0 seconds as "0:00".
        """

        result = _format_time(0)

        self.assertEqual(
            result,
            "0:00",
            _color_error_message_in_red(
                f'_format_time(0) should return "0:00" instead of "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_seconds_only_are_zero_padded(self) -> None:

        """
        Test that _format_time() zero-pads seconds below 10.
        """

        result = _format_time(45)

        self.assertEqual(
            result,
            "0:45",
            _color_error_message_in_red(
                f'_format_time(45) should return "0:45" instead of "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_exact_minute_formats_correctly(self) -> None:

        """
        Test that _format_time() formats exactly 60 seconds as "1:00".
        """

        result = _format_time(60)

        self.assertEqual(
            result,
            "1:00",
            _color_error_message_in_red(
                f'_format_time(60) should return "1:00" instead of "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_minutes_and_seconds_format_correctly(self) -> None:

        """
        Test that _format_time() formats mixed minutes and seconds correctly.
        """

        result = _format_time(225)

        self.assertEqual(
            result,
            "3:45",
            _color_error_message_in_red(
                f'_format_time(225) should return "3:45" instead of "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_exact_hour_formats_with_hours_prefix(self) -> None:

        """
        Test that _format_time() switches to H:MM:SS format at exactly 1 hour.
        """

        result = _format_time(3600)

        self.assertEqual(
            result,
            "1:00:00",
            _color_error_message_in_red(
                f'_format_time(3600) should return "1:00:00" instead of "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_hours_minutes_seconds_all_format_correctly(self) -> None:

        """
        Test that _format_time() formats hours, minutes, and seconds all correctly.
        """

        result = _format_time(3723)

        self.assertEqual(
            result,
            "1:02:03",
            _color_error_message_in_red(
                f'_format_time(3723) should return "1:02:03" instead of "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_float_input_is_truncated_to_int(self) -> None:

        """
        Test that _format_time() truncates float input to integer seconds.
        """

        result = _format_time(90.9)

        self.assertEqual(
            result,
            "1:30",
            _color_error_message_in_red(
                f'_format_time(90.9) should return "1:30" instead of "{result}".'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
