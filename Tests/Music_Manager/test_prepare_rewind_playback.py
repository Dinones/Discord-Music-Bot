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

class Test_Prepare_Rewind_Playback(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_places_song_at_front_of_priority_queue(self) -> None:

        song = {"title": "Rewind Copy", "seek_offset": 40}

        await self.manager.prepare_rewind_playback(song)

        self.assertEqual(
            self.manager.priority_queue[0],
            song,
            _color_error_message_in_red(
                'prepare_rewind_playback() should insert the song at position 0 of the priority queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_clears_current_song_sentinel(self) -> None:

        self.manager.current_song = {"title": "Playing"}

        await self.manager.prepare_rewind_playback({"title": "Rewind Copy", "seek_offset": 40})

        self.assertIsNone(
            self.manager.current_song,
            _color_error_message_in_red(
                'prepare_rewind_playback() should set current_song to None to prevent mark_song_played from firing.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_song_goes_to_front_when_priority_queue_already_has_items(self) -> None:

        existing = {"title": "Already Queued"}
        rewind   = {"title": "Rewind Copy", "seek_offset": 20}

        self.manager.priority_queue.append(existing)
        await self.manager.prepare_rewind_playback(rewind)

        self.assertEqual(
            self.manager.priority_queue[0],
            rewind,
            _color_error_message_in_red(
                'prepare_rewind_playback() should place the rewind song before any existing priority queue items.'
            )
        )
        self.assertEqual(
            self.manager.priority_queue[1],
            existing,
            _color_error_message_in_red(
                'prepare_rewind_playback() should not discard existing priority queue items.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
