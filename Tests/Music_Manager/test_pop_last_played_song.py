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

class Test_Pop_Last_Played_Song(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_pop_last_played_song_returns_none_when_played_queue_empty(self) -> None:

        result = await self.manager.pop_last_played_song()

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'pop_last_played_song() should return None when the played queue is empty.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_pop_last_played_song_returns_most_recently_played(self) -> None:

        first  = {"title": "First"}
        second = {"title": "Second"}
        self.manager.played_queue.append(first)
        self.manager.played_queue.append(second)

        result = await self.manager.pop_last_played_song()

        self.assertEqual(
            result,
            second,
            _color_error_message_in_red(
                'pop_last_played_song() should return the last (most recently played) song.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_pop_last_played_song_removes_song_from_played_queue(self) -> None:

        song = {"title": "Played"}
        self.manager.played_queue.append(song)

        await self.manager.pop_last_played_song()

        self.assertEqual(
            len(self.manager.played_queue),
            0,
            _color_error_message_in_red(
                'pop_last_played_song() should remove the song from the played queue.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
