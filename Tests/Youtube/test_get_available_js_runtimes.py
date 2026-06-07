###########################################################################################################################
#   Tests for _get_available_js_runtimes() in Utils/Youtube.                                                             #
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
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Get_Available_JS_Runtimes(unittest.TestCase):

    def test_returns_empty_dict_when_no_runtimes_installed(self) -> None:

        """
        Test that _get_available_js_runtimes() returns an empty dict when no JS runtimes are found.
        """

        with patch("Utils.Youtube.shutil.which", return_value = None):
            result = Utils.Youtube._get_available_js_runtimes()

        self.assertEqual(
            result,
            {},
            _color_error_message_in_red(
                '_get_available_js_runtimes() should return an empty dict when no runtimes are installed.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_only_installed_runtimes(self) -> None:

        """
        Test that _get_available_js_runtimes() only includes runtimes that shutil.which finds.
        """

        def _mock_which(runtime: str) -> str:
            return "/usr/bin/node" if runtime == "node" else None

        with patch("Utils.Youtube.shutil.which", side_effect = _mock_which):
            result = Utils.Youtube._get_available_js_runtimes()

        self.assertIn(
            "node",
            result,
            _color_error_message_in_red(
                '_get_available_js_runtimes() should include "node" when it is installed.'
            )
        )

        for runtime in ("deno", "quickjs", "bun"):
            self.assertNotIn(
                runtime,
                result,
                _color_error_message_in_red(
                    f'_get_available_js_runtimes() should not include "{runtime}" when it is not installed.'
                )
            )

    #######################################################################################################################
    #######################################################################################################################

    def test_each_runtime_maps_to_empty_config_dict(self) -> None:

        """
        Test that _get_available_js_runtimes() maps each found runtime to an empty dict as yt-dlp expects.
        """

        with patch("Utils.Youtube.shutil.which", return_value = "/usr/bin/runtime"):
            result = Utils.Youtube._get_available_js_runtimes()

        for runtime, config in result.items():
            self.assertEqual(
                config,
                {},
                _color_error_message_in_red(
                    f'_get_available_js_runtimes() should map "{runtime}" to an empty dict, got "{config}".'
                )
            )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_all_runtimes_when_all_installed(self) -> None:

        """
        Test that _get_available_js_runtimes() includes all supported runtimes when all are installed.
        """

        with patch("Utils.Youtube.shutil.which", return_value = "/usr/bin/runtime"):
            result = Utils.Youtube._get_available_js_runtimes()

        for runtime in ("deno", "node", "quickjs", "bun"):
            self.assertIn(
                runtime,
                result,
                _color_error_message_in_red(
                    f'_get_available_js_runtimes() should include "{runtime}" when it is installed.'
                )
            )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
