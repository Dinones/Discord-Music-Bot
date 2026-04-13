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
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Youtube
import Utils.Constants as CONST
from Utils.Music_Manager import Music_Manager
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Configure_YTDL(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self._music_manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    def test_configure_ytdl_sets_expected_base_options(self) -> None:

        """
        Test that configure_ytdl() sets the expected yt-dlp options.
        """

        # Force os.path.exists() to return always False and disable the print() function  
        with (
            patch("Utils.Youtube.os.path.exists", return_value = False),
            patch("Utils.Youtube.print")
        ):
            Utils.Youtube.configure_ytdl(self._music_manager)

        keys = set(self._music_manager.ytdl_options)

        # Check all options are initialized
        for option in (
            "format", "default_search", "skip_download", "noprogress", "noplaylist", "writedescription", "quiet",
            "verbose", "no_warnings", "logger", "postprocessors"
        ):
            self.assertIn(
                option,
                keys,
                _color_error_message_in_red(f'Option "{option}" not found after initializing ytdl_options.')
            )

    #######################################################################################################################
    #######################################################################################################################

    def test_configure_ytdl_adds_cookiefile_when_file_exists(self) -> None:

        """
        Test that configure_ytdl() adds the cookie file option when cookies file exists.
        """

        expected_cookie_path = os.path.abspath(
            os.path.join(os.path.dirname(Utils.Youtube.__file__), "..", CONST.YT_COOKIES_FILE_PATH)
        )

        # Force os.path.exists() to return always True
        with patch("Utils.Youtube.os.path.exists", return_value = True):
            Utils.Youtube.configure_ytdl(self._music_manager)

        # Check the "cookiefile" option has been added to ytdl_options
        self.assertEqual(
            self._music_manager.ytdl_options.get("cookiefile"),
            expected_cookie_path,
            _color_error_message_in_red(
                f'The cookies file was found, but path was not added to ytdl_options "{expected_cookie_path}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_configure_ytdl_prints_warning_when_cookiefile_missing(self) -> None:

        """
        Test that configure_ytdl() prints a warning when cookies file is missing.
        """

        # Force os.path.exists() to return always False and redirect the print() function to mock_print() to store data  
        with (
            patch("Utils.Youtube.os.path.exists", return_value = False),
            patch("Utils.Youtube.print") as mock_print
        ):
            Utils.Youtube.configure_ytdl(self._music_manager)

        # Check the "cookiefile" option has not been added to ytdl_options
        self.assertNotIn(
            "cookiefile",
            self._music_manager.ytdl_options,
            _color_error_message_in_red(
                f'The "cookiefile" option has been added to ytdl_options although the cookies file does not exist.'
            )
        )

        # Check the warning logging message is printed in terminal
        self.assertEqual(
            mock_print.call_count,
            1,
            _color_error_message_in_red(f'Exactly ONE warning logging message should have been printed in terminal.')
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)