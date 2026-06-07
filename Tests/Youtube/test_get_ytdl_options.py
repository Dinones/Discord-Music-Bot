###########################################################################################################################
#   Tests for _get_ytdl_options() in Utils/Youtube.                                                                      #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Youtube
from Utils.Music_Manager import Music_Manager
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Get_YTDL_Options(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self._music_manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    def test_get_ytdl_options_applies_overrides_without_mutating_original(self) -> None:

        """
        Test that _get_ytdl_options() applies overrides and does not mutate original base options.
        """

        options = Utils.Youtube._get_ytdl_options(
            Music_Manager  = self._music_manager,
            default_search = "ytsearch2",
            skip_download  = False
        )

        self.assertEqual(
            options.get("default_search"),
            "ytsearch2",
            _color_error_message_in_red(
                f'The "default_search" value of "ytdl_options" returned by the "_get_ytdl_options()" function should ' +
                f'have been set to "ytsearch2" instead of "{options.get("default_search")}".'
            )
        )

        self.assertFalse(
            options.get("skip_download"),
            _color_error_message_in_red(
                f'The "skip_download" value of "ytdl_options" returned by the "_get_ytdl_options()" function should ' +
                f'have been set to "False" instead of "{options.get("skip_download")}".'
            )
        )

        self.assertEqual(
            self._music_manager.ytdl_options.get("default_search"),
            "auto",
            _color_error_message_in_red(
                f'The "default_search" value of the original "Music_Manager.ytdl_options" should have not changed from ' +
                f'"auto" to "{self._music_manager.ytdl_options.get("default_search")}" after calling the ' + 
                f'"_get_ytdl_options()" function.'
            )
        )
        self.assertTrue(
            self._music_manager.ytdl_options.get("skip_download"),
            _color_error_message_in_red(
                f'The "skip_download" value of the original "Music_Manager.ytdl_options" should have not changed from ' +
                f'"True" to "{self._music_manager.ytdl_options.get("skip_download")}" after calling the ' + 
                f'"_get_ytdl_options()" function.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_ytdl_options_returns_deep_copy_for_nested_values(self) -> None:

        """
        Test that _get_ytdl_options() deep-copies nested values like postprocessors.
        """

        self._music_manager.ytdl_options = {"postprocessors": [{"preferredcodec": "mp3"}]}

        options = Utils.Youtube._get_ytdl_options(self._music_manager)
        options["postprocessors"][0]["preferredcodec"] = "wav"

        self.assertEqual(
            self._music_manager.ytdl_options["postprocessors"][0]["preferredcodec"],
            "mp3",
            _color_error_message_in_red(
                f'Values of the original "Music_Manager.ytdl_options" should have not changed from ' +
                f'"mp3" to "{self._music_manager.ytdl_options["postprocessors"][0]["preferredcodec"]}" after editing ' + 
                f'the values that "_get_ytdl_options()" function returned.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)