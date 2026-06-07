###########################################################################################################################
#   Tests for Music_Manager.enqueue_priority_song().                                                                     #
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

class Test_Enqueue_Priority_Song(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_enqueue_priority_song_appends_to_priority_queue(self) -> None:

        song = {"title": "Priority Song"}
        await self.manager.enqueue_priority_song(song)

        self.assertIn(
            song,
            self.manager.priority_queue,
            _color_error_message_in_red(
                'enqueue_priority_song() should append the song to the priority queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_enqueue_priority_song_returns_priority_queue_size(self) -> None:

        size = await self.manager.enqueue_priority_song({"title": "Song A"})

        self.assertEqual(
            size,
            1,
            _color_error_message_in_red(
                'enqueue_priority_song() should return the priority queue size after insertion.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_enqueue_priority_song_maintains_insertion_order(self) -> None:

        song_a = {"title": "A"}
        song_b = {"title": "B"}
        await self.manager.enqueue_priority_song(song_a)
        await self.manager.enqueue_priority_song(song_b)

        self.assertEqual(
            list(self.manager.priority_queue),
            [song_a, song_b],
            _color_error_message_in_red(
                'Songs should be appended in insertion order to the priority queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_enqueue_priority_song_does_not_affect_normal_queue(self) -> None:

        self.manager.queue.append({"title": "Normal"})
        await self.manager.enqueue_priority_song({"title": "Priority"})

        self.assertEqual(
            len(self.manager.queue),
            1,
            _color_error_message_in_red(
                'enqueue_priority_song() should not modify the normal queue.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
