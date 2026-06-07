###########################################################################################################################
#   Tests for Music_Manager.push_song_front().                                                                           #
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

class Test_Push_Song_Front(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_push_song_front_prepends_to_normal_queue(self) -> None:

        existing = {"title": "Existing"}
        front    = {"title": "Front"}
        self.manager.queue.append(existing)

        await self.manager.push_song_front(front)

        self.assertEqual(
            self.manager.queue[0],
            front,
            _color_error_message_in_red(
                'push_song_front() should place the song at position 0 of the normal queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_push_song_front_clears_current_song(self) -> None:

        self.manager.current_song = {"title": "Was Playing"}
        await self.manager.push_song_front({"title": "Reinserted"})

        self.assertIsNone(
            self.manager.current_song,
            _color_error_message_in_red(
                'push_song_front() should clear current_song.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
