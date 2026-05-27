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

class Test_Get_Full_Queue_Snapshot(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_none_current_song_when_idle(self) -> None:

        current, _, _ = await self.manager.get_full_queue_snapshot()

        self.assertIsNone(
            current,
            _color_error_message_in_red(
                'get_full_queue_snapshot() should return None for current_song when the bot is idle.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_current_song_when_set(self) -> None:

        song = {"title": "Playing"}
        self.manager.current_song = song

        current, _, _ = await self.manager.get_full_queue_snapshot()

        self.assertEqual(
            current,
            song,
            _color_error_message_in_red(
                'get_full_queue_snapshot() should return the current_song value.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_priority_and_normal_queues_as_lists(self) -> None:

        priority_song = {"title": "Priority"}
        normal_song   = {"title": "Normal"}
        self.manager.priority_queue.append(priority_song)
        self.manager.queue.append(normal_song)

        _, priority, normal = await self.manager.get_full_queue_snapshot()

        self.assertEqual(
            priority,
            [priority_song],
            _color_error_message_in_red(
                'get_full_queue_snapshot() should return the priority queue as a list.'
            )
        )
        self.assertEqual(
            normal,
            [normal_song],
            _color_error_message_in_red(
                'get_full_queue_snapshot() should return the normal queue as a list.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_snapshot_is_independent_copy(self) -> None:

        self.manager.queue.append({"title": "A"})
        self.manager.priority_queue.append({"title": "B"})

        _, priority, normal = await self.manager.get_full_queue_snapshot()
        priority.clear()
        normal.clear()

        self.assertEqual(
            len(self.manager.priority_queue),
            1,
            _color_error_message_in_red(
                'Modifying the priority snapshot should not affect the actual priority queue.'
            )
        )
        self.assertEqual(
            len(self.manager.queue),
            1,
            _color_error_message_in_red(
                'Modifying the normal snapshot should not affect the actual normal queue.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
