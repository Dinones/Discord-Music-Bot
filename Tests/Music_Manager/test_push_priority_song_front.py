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

class Test_Push_Priority_Song_Front(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_push_priority_song_front_prepends_to_priority_queue(self) -> None:

        existing = {"title": "Existing Priority"}
        front    = {"title": "New Front"}
        self.manager.priority_queue.append(existing)

        await self.manager.push_priority_song_front(front)

        self.assertEqual(
            self.manager.priority_queue[0],
            front,
            _color_error_message_in_red(
                'push_priority_song_front() should place the song at position 0 of the priority queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_push_priority_song_front_preserves_existing_songs(self) -> None:

        existing = {"title": "Existing"}
        front    = {"title": "Front"}
        self.manager.priority_queue.append(existing)

        await self.manager.push_priority_song_front(front)

        self.assertEqual(
            len(self.manager.priority_queue),
            2,
            _color_error_message_in_red(
                'push_priority_song_front() should not remove existing songs from the priority queue.'
            )
        )
        self.assertEqual(
            self.manager.priority_queue[1],
            existing,
            _color_error_message_in_red(
                'The previously existing song should remain at position 1.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_push_priority_song_front_returns_priority_queue_size(self) -> None:

        await self.manager.push_priority_song_front({"title": "First"})
        size = await self.manager.push_priority_song_front({"title": "Second"})

        self.assertEqual(
            size,
            2,
            _color_error_message_in_red(
                'push_priority_song_front() should return the priority queue size after insertion.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_push_priority_song_front_does_not_affect_normal_queue(self) -> None:

        self.manager.queue.append({"title": "Normal"})
        await self.manager.push_priority_song_front({"title": "Priority Front"})

        self.assertEqual(
            len(self.manager.queue),
            1,
            _color_error_message_in_red(
                'push_priority_song_front() should not modify the normal queue.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
