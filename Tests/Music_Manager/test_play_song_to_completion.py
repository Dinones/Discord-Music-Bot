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
        mock_manager = Mock()

        mock_updater              = Mock(start = AsyncMock(), stop = AsyncMock())
        mock_updater._paused_acc  = 0.0
        mock_updater._seek_offset = 0

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

    #######################################################################################################################
    #######################################################################################################################

    async def test_player_read_is_called_when_not_already_warmed(self) -> None:

        voice_client, loop                              = self._build_voice_client()
        message, song, player, mock_updater, mock_manager = self._build_mocks()

        with (
            patch("Utils.Music_Manager.Now_Playing_Updater", return_value = mock_updater),
            patch("Utils.Music_Manager.get_music_manager", return_value = mock_manager)
        ):
            await self._play_song_to_completion(
                voice_client, player, song, message, loop, already_warmed = False
            )

        player.read.assert_called_once()

        self.assertEqual(
            player.read.call_count,
            1,
            _color_error_message_in_red(
                '_play_song_to_completion() should call player.read() once via run_in_executor to pre-warm '
                'the FFmpeg pipeline when already_warmed=False.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_player_read_is_not_called_when_already_warmed(self) -> None:

        voice_client, loop                              = self._build_voice_client()
        message, song, player, mock_updater, mock_manager = self._build_mocks()

        with (
            patch("Utils.Music_Manager.Now_Playing_Updater", return_value = mock_updater),
            patch("Utils.Music_Manager.get_music_manager", return_value = mock_manager)
        ):
            await self._play_song_to_completion(
                voice_client, player, song, message, loop, already_warmed = True
            )

        player.read.assert_not_called()

        self.assertEqual(
            player.read.call_count,
            0,
            _color_error_message_in_red(
                '_play_song_to_completion() should skip player.read() when already_warmed=True '
                'to avoid discarding audio frames that were already consumed during pre-warming.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
