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

class Test_Peek_Next_Song(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_peek_next_song_returns_none_when_all_queues_empty(self) -> None:

        result = await self.manager.peek_next_song()

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'peek_next_song() should return None when both queues are empty.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_peek_next_song_returns_priority_song_before_normal_song(self) -> None:

        normal   = {"title": "Normal"}
        priority = {"title": "Priority"}
        self.manager.queue.append(normal)
        self.manager.priority_queue.append(priority)

        result = await self.manager.peek_next_song()

        self.assertEqual(
            result,
            priority,
            _color_error_message_in_red(
                'peek_next_song() should return from the priority queue first.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_peek_next_song_does_not_remove_song_from_queue(self) -> None:

        song = {"title": "Song"}
        self.manager.queue.append(song)

        await self.manager.peek_next_song()

        self.assertEqual(
            len(self.manager.queue),
            1,
            _color_error_message_in_red(
                'peek_next_song() should not remove the song from the queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_peek_next_song_returns_normal_song_when_priority_empty(self) -> None:

        song = {"title": "Normal"}
        self.manager.queue.append(song)

        result = await self.manager.peek_next_song()

        self.assertEqual(
            result,
            song,
            _color_error_message_in_red(
                'peek_next_song() should return from the normal queue when priority queue is empty.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
