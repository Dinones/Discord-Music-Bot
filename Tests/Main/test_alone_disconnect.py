###########################################################################################################################
#   Tests for _alone_disconnect() in Main.                                                                               #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Main
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Alone_Disconnect(unittest.IsolatedAsyncioTestCase):

    def _build_voice_client(self, is_playing: bool = False, is_paused: bool = False) -> Mock:

        return Mock(
            is_playing = Mock(return_value = is_playing),
            is_paused  = Mock(return_value = is_paused),
            stop       = Mock(),
            disconnect = AsyncMock()
        )

    #######################################################################################################################
    #######################################################################################################################

    def _build_music_manager(self, last_text_channel: Mock = None) -> Mock:

        mm                    = Mock()
        mm.clear_all_queues   = AsyncMock()
        mm.alone_timeout_task = Mock()
        mm.last_text_channel  = last_text_channel

        return mm

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_early_on_cancellation_without_disconnecting(self) -> None:

        vc = self._build_voice_client()
        mm = self._build_music_manager()

        task = asyncio.create_task(Main._alone_disconnect(vc, mm))
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        vc.disconnect.assert_not_called()
        mm.clear_all_queues.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_stops_playback_when_voice_client_is_playing_on_timeout(self) -> None:

        vc = self._build_voice_client(is_playing = True)
        mm = self._build_music_manager()

        with patch("asyncio.sleep", new = AsyncMock()):
            with patch("Main.print"):
                await Main._alone_disconnect(vc, mm)

        vc.stop.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_stops_playback_when_voice_client_is_paused_on_timeout(self) -> None:

        vc = self._build_voice_client(is_paused = True)
        mm = self._build_music_manager()

        with patch("asyncio.sleep", new = AsyncMock()):
            with patch("Main.print"):
                await Main._alone_disconnect(vc, mm)

        vc.stop.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_does_not_stop_when_voice_client_is_idle_on_timeout(self) -> None:

        vc = self._build_voice_client()
        mm = self._build_music_manager()

        with patch("asyncio.sleep", new = AsyncMock()):
            with patch("Main.print"):
                await Main._alone_disconnect(vc, mm)

        vc.stop.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_clears_all_queues_on_timeout(self) -> None:

        vc = self._build_voice_client()
        mm = self._build_music_manager()

        with patch("asyncio.sleep", new = AsyncMock()):
            with patch("Main.print"):
                await Main._alone_disconnect(vc, mm)

        mm.clear_all_queues.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_disconnects_voice_client_on_timeout(self) -> None:

        vc = self._build_voice_client()
        mm = self._build_music_manager()

        with patch("asyncio.sleep", new = AsyncMock()):
            with patch("Main.print"):
                await Main._alone_disconnect(vc, mm)

        vc.disconnect.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_clears_alone_timeout_task_on_timeout(self) -> None:

        vc = self._build_voice_client()
        mm = self._build_music_manager()

        with patch("asyncio.sleep", new = AsyncMock()):
            with patch("Main.print"):
                await Main._alone_disconnect(vc, mm)

        self.assertIsNone(
            mm.alone_timeout_task,
            _color_error_message_in_red(
                '_alone_disconnect() should set alone_timeout_task to None after disconnecting.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_message_to_last_text_channel_on_timeout(self) -> None:

        channel = Mock(send = AsyncMock())
        vc      = self._build_voice_client()
        mm      = self._build_music_manager(last_text_channel = channel)

        with patch("asyncio.sleep", new = AsyncMock()):
            with patch("Main.print"):
                await Main._alone_disconnect(vc, mm)

        channel.send.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_does_not_send_message_when_no_last_text_channel(self) -> None:

        vc = self._build_voice_client()
        mm = self._build_music_manager(last_text_channel = None)

        with patch("asyncio.sleep", new = AsyncMock()):
            with patch("Main.print"):
                await Main._alone_disconnect(vc, mm)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
