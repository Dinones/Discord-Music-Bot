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

class Test_Enqueue_Songs(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_enqueue_songs_appends_to_queue(self) -> None:

        songs = [{"title": "Song 1", "source_type": "Youtube"}]
        await self.manager.enqueue_songs(songs)

        self.assertEqual(
            len(self.manager.queue),
            1,
            _color_error_message_in_red(
                'Queue should contain exactly 1 song after enqueue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_enqueue_songs_returns_combined_queue_size(self) -> None:

        from collections import deque
        self.manager.priority_queue = deque([{"title": "Priority"}])
        songs = [{"title": "Normal"}]
        size = await self.manager.enqueue_songs(songs)

        self.assertEqual(
            size,
            2,
            _color_error_message_in_red(
                'Returned size should include both priority and normal queues.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_enqueue_songs_appends_multiple_songs_in_order(self) -> None:

        songs = [{"title": "A"}, {"title": "B"}, {"title": "C"}]
        await self.manager.enqueue_songs(songs)

        self.assertEqual(
            list(self.manager.queue),
            songs,
            _color_error_message_in_red(
                'Songs should be appended to the queue in the order they were provided.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
