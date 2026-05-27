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

        with (
            patch("Utils.Youtube.os.path.exists", return_value = False),
            patch("Utils.Youtube.get_youtube_cookies"),
            patch("Utils.Youtube.print")
        ):
            Utils.Youtube.configure_ytdl(self._music_manager)

        keys = set(self._music_manager.ytdl_options)

        for option in (
            "format", "default_search", "skip_download", "noprogress", "noplaylist", "writedescription", "quiet",
            "verbose", "no_warnings", "logger", "postprocessors"
        ):
            self.assertIn(
                option,
                keys,
                _color_error_message_in_red(
                    f'Option "{option}" not found after initializing ytdl_options.'
                )
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

        with patch("Utils.Youtube.os.path.exists", return_value = True):
            Utils.Youtube.configure_ytdl(self._music_manager)

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

        with (
            patch("Utils.Youtube.os.path.exists", return_value = False),
            patch("Utils.Youtube.get_youtube_cookies"),
            patch("Utils.Youtube.print") as mock_print
        ):
            Utils.Youtube.configure_ytdl(self._music_manager)

        self.assertNotIn(
            "cookiefile",
            self._music_manager.ytdl_options,
            _color_error_message_in_red(
                f'The "cookiefile" option has been added to ytdl_options although the cookies file does not exist.'
            )
        )

        self.assertEqual(
            mock_print.call_count,
            2,
            _color_error_message_in_red(
                f'Exactly TWO warning logging messages should have been printed in terminal.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_configure_ytdl_adds_available_js_runtime(self) -> None:

        """
        Test that configure_ytdl() adds an installed JavaScript runtime for yt-dlp challenge solving.
        """

        def mock_which(binary: str) -> str:
            return f"/usr/bin/{binary}" if binary == "node" else None

        with (
            patch("Utils.Youtube.os.path.exists", return_value = False),
            patch("Utils.Youtube.shutil.which", side_effect = mock_which),
            patch("Utils.Youtube.get_youtube_cookies"),
            patch("Utils.Youtube.print")
        ):
            Utils.Youtube.configure_ytdl(self._music_manager)

        self.assertEqual(
            self._music_manager.ytdl_options.get("js_runtimes"),
            {"node": {}},
            _color_error_message_in_red(
                f'The "node" JavaScript runtime should have been added to ytdl_options when available.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
