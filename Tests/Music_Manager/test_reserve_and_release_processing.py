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

from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Reserve_And_Release_Processing(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_reserve_processing_returns_true_when_not_processing(self) -> None:

        result = await self.manager.reserve_processing()

        self.assertTrue(
            result,
            _color_error_message_in_red(
                'reserve_processing() should return True when no worker is active.'
            )
        )
        self.assertTrue(
            self.manager.is_processing,
            _color_error_message_in_red(
                'is_processing flag should be set to True after reservation.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_reserve_processing_returns_false_when_already_processing(self) -> None:

        await self.manager.reserve_processing()
        result = await self.manager.reserve_processing()

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'reserve_processing() should return False when a worker is already active.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_release_processing_clears_flag_and_current_song(self) -> None:

        self.manager.is_processing = True
        self.manager.current_song  = {"title": "Playing Song"}

        await self.manager.release_processing()

        self.assertFalse(
            self.manager.is_processing,
            _color_error_message_in_red(
                'is_processing should be False after release.'
            )
        )
        self.assertIsNone(
            self.manager.current_song,
            _color_error_message_in_red(
                'current_song should be None after release.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
