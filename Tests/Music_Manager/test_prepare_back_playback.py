###########################################################################################################################
#   Tests for Music_Manager.prepare_back_playback().                                                                     #
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

class Test_Prepare_Back_Playback(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_places_previous_song_at_front_and_current_song_behind_it(self) -> None:

        previous = {"title": "Previous"}
        current  = {"title": "Current"}

        await self.manager.prepare_back_playback(previous, current)

        self.assertEqual(
            self.manager.priority_queue[0],
            previous,
            _color_error_message_in_red(
                'prepare_back_playback() should place the previous song at position 0.'
            )
        )
        self.assertEqual(
            self.manager.priority_queue[1],
            current,
            _color_error_message_in_red(
                'prepare_back_playback() should place the current song at position 1.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_skips_current_song_when_none(self) -> None:

        previous = {"title": "Previous"}

        await self.manager.prepare_back_playback(previous, None)

        self.assertEqual(
            len(self.manager.priority_queue),
            1,
            _color_error_message_in_red(
                'prepare_back_playback() should only add one song when current_song is None.'
            )
        )
        self.assertEqual(
            self.manager.priority_queue[0],
            previous,
            _color_error_message_in_red(
                'prepare_back_playback() should place the previous song at position 0 when current_song is None.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_clears_current_song_sentinel(self) -> None:

        self.manager.current_song = {"title": "Playing"}

        await self.manager.prepare_back_playback({"title": "Previous"}, {"title": "Current"})

        self.assertIsNone(
            self.manager.current_song,
            _color_error_message_in_red(
                'prepare_back_playback() should set current_song to None to prevent mark_song_played from firing.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
