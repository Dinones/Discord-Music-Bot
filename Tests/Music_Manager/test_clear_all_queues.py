###########################################################################################################################
#   Tests for Music_Manager.clear_all_queues().                                                                          #
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

class Test_Clear_All_Queues(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_clear_all_queues_empties_all_deques_and_current_song(self) -> None:

        self.manager.queue.append({"title": "A"})
        self.manager.priority_queue.append({"title": "B"})
        self.manager.played_queue.append({"title": "C"})
        self.manager.current_song = {"title": "D"}

        await self.manager.clear_all_queues()

        self.assertEqual(
            len(self.manager.queue),
            0,
            _color_error_message_in_red(
                'Normal queue should be empty after clear.'
            )
        )
        self.assertEqual(
            len(self.manager.priority_queue),
            0,
            _color_error_message_in_red(
                'Priority queue should be empty after clear.'
            )
        )
        self.assertEqual(
            len(self.manager.played_queue),
            0,
            _color_error_message_in_red(
                'Played queue should be empty after clear.'
            )
        )
        self.assertIsNone(
            self.manager.current_song,
            _color_error_message_in_red(
                'current_song should be None after clear.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_clear_all_queues_sets_was_cleared_flag(self) -> None:

        self.manager.was_cleared = False

        await self.manager.clear_all_queues()

        self.assertTrue(
            self.manager.was_cleared,
            _color_error_message_in_red(
                'clear_all_queues() should set was_cleared to True so callers can suppress the QUEUE_FINISHED message.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
