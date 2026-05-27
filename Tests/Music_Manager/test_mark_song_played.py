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

class Test_Mark_Song_Played(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_mark_song_played_appends_to_played_queue(self) -> None:

        song = {"title": "Finished"}
        await self.manager.mark_song_played(song)

        self.assertIn(
            song,
            self.manager.played_queue,
            _color_error_message_in_red(
                'mark_song_played() should append the song to the played queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_mark_song_played_clears_current_song(self) -> None:

        song = {"title": "Finished"}
        self.manager.current_song = song

        await self.manager.mark_song_played(song)

        self.assertIsNone(
            self.manager.current_song,
            _color_error_message_in_red(
                'mark_song_played() should set current_song to None.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
