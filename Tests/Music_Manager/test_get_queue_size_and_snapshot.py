###########################################################################################################################
#   Tests for Music_Manager.get_queue_size() and get_queue_snapshot().                                                   #
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

class Test_Get_Queue_Size_And_Snapshot(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_get_queue_size_returns_correct_count(self) -> None:

        self.manager.queue.append({"title": "A"})
        self.manager.queue.append({"title": "B"})

        result = await self.manager.get_queue_size()

        self.assertEqual(
            result,
            2,
            _color_error_message_in_red(
                'get_queue_size() should return the number of songs in the normal queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_get_queue_snapshot_returns_copy_of_queue(self) -> None:

        songs = [{"title": "A"}, {"title": "B"}]
        for song in songs:
            self.manager.queue.append(song)

        snapshot = await self.manager.get_queue_snapshot()

        self.assertEqual(
            snapshot,
            songs,
            _color_error_message_in_red(
                'get_queue_snapshot() should return a list matching the queue contents.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_get_queue_snapshot_is_independent_copy(self) -> None:

        self.manager.queue.append({"title": "A"})

        snapshot = await self.manager.get_queue_snapshot()
        snapshot.clear()

        self.assertEqual(
            len(self.manager.queue),
            1,
            _color_error_message_in_red(
                'Modifying the snapshot should not affect the actual queue.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
