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

class Test_Shuffle_Normal_Queue(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_shuffle_returns_zero_when_queue_empty(self) -> None:

        result = await self.manager.shuffle_normal_queue()

        self.assertEqual(
            result,
            0,
            _color_error_message_in_red(
                'shuffle_normal_queue() should return 0 when the queue is empty.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_shuffle_returns_one_without_modifying_single_song(self) -> None:

        song = {"title": "Only"}
        self.manager.queue.append(song)

        result = await self.manager.shuffle_normal_queue()

        self.assertEqual(
            result,
            1,
            _color_error_message_in_red(
                'shuffle_normal_queue() should return 1 for a single-song queue.'
            )
        )
        self.assertEqual(
            self.manager.queue[0],
            song,
            _color_error_message_in_red(
                'The single song should remain unchanged.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_shuffle_returns_correct_count_and_preserves_all_songs(self) -> None:

        songs = [{"title": f"Song {i}"} for i in range(5)]
        for song in songs:
            self.manager.queue.append(song)

        result = await self.manager.shuffle_normal_queue()

        self.assertEqual(
            result,
            5,
            _color_error_message_in_red(
                'shuffle_normal_queue() should return the number of songs in the queue.'
            )
        )
        self.assertEqual(
            len(self.manager.queue),
            5,
            _color_error_message_in_red(
                'Queue size should remain unchanged after shuffle.'
            )
        )
        for song in songs:
            self.assertIn(
                song,
                self.manager.queue,
                _color_error_message_in_red(
                    f'Song "{song["title"]}" should still be present in the queue after shuffle.'
                )
            )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
