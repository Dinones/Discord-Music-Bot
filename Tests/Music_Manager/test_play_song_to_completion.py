###########################################################################################################################
#   Tests for _play_song_to_completion() in Music_Manager.                                                               #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
import unittest
from unittest.mock import Mock, AsyncMock, patch
from typing import Any, Dict, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Play_Song_To_Completion(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import _play_song_to_completion
            self._play_song_to_completion = _play_song_to_completion

    #######################################################################################################################
    #######################################################################################################################

    def _build_voice_client(self) -> Tuple[Mock, asyncio.AbstractEventLoop]:

        loop = asyncio.get_event_loop()

        def _fake_play(audio_source, after):
            # Fire the after-callback on the event loop immediately so the coroutine unblocks
            loop.call_soon_threadsafe(after, None)

        voice_client = Mock(
            play      = _fake_play,
            is_paused = Mock(return_value = False)
        )

        return voice_client, loop

    #######################################################################################################################
    #######################################################################################################################

    def _build_mocks(self) -> Tuple[Mock, Dict[str, Any], Mock, Mock, Mock]:

        message      = Mock(delete = AsyncMock())
        song         = {"title": "Test Song", "duration": 300}
        player       = Mock()
        mock_updater = Mock(start = AsyncMock(), stop = AsyncMock())
        mock_manager = Mock()

        return message, song, player, mock_updater, mock_manager

    #######################################################################################################################
    #######################################################################################################################

    async def test_delete_is_called_when_song_ends(self) -> None:

        voice_client, loop                              = self._build_voice_client()
        message, song, player, mock_updater, mock_manager = self._build_mocks()

        with (
            patch("Utils.Music_Manager.Now_Playing_Updater", return_value = mock_updater),
            patch("Utils.Music_Manager.get_music_manager", return_value = mock_manager)
        ):
            await self._play_song_to_completion(voice_client, player, song, message, loop)

        message.delete.assert_called_once()

        self.assertEqual(
            message.delete.call_count,
            1,
            _color_error_message_in_red(
                '_play_song_to_completion() should call message.delete() exactly once when the song ends.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_logs_when_delete_raises(self) -> None:

        voice_client, loop                              = self._build_voice_client()
        message, song, player, mock_updater, mock_manager = self._build_mocks()
        message.delete                                  = AsyncMock(side_effect = Exception("Missing Permissions"))

        with (
            patch("Utils.Music_Manager.Now_Playing_Updater", return_value = mock_updater),
            patch("Utils.Music_Manager.get_music_manager", return_value = mock_manager),
            patch("Utils.Music_Manager.save_exception_to_txt") as mock_save_exception,
            patch("Utils.Music_Manager.print")
        ):
            await self._play_song_to_completion(voice_client, player, song, message, loop)

        self.assertEqual(
            mock_save_exception.call_count,
            1,
            _color_error_message_in_red(
                '_play_song_to_completion() should call save_exception_to_txt() exactly once when delete() fails.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
