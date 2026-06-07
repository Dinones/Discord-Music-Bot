###########################################################################################################################
#   Tests for the !clear and !stop Discord bot commands.                                                                 #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from typing import Any, Callable
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Commands.Clear
import Utils.Constants as CONST
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class _Fake_Bot:

    def __init__(self) -> None:
        self.registered_commands = {}

    #######################################################################################################################
    #######################################################################################################################

    def command(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:

        def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
            command_name = kwargs.get("name", function.__name__)
            self.registered_commands[command_name] = function
            return function

        return decorator

###########################################################################################################################
###########################################################################################################################

class Test_Register_Clear_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Clear.register_clear_command(self.bot)
        self.clear_command = self.bot.registered_commands.get("clear")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self, is_playing: bool = False, is_paused: bool = False) -> Mock:

        context = Mock(
            send         = AsyncMock(),
            guild        = Mock(),
            author       = Mock(),
            voice_client = Mock(
                is_connected = Mock(return_value = True),
                is_playing   = Mock(return_value = is_playing),
                is_paused    = Mock(return_value = is_paused),
                stop         = Mock()
            )
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME

        return context

    #######################################################################################################################
    #######################################################################################################################

    def _build_mock_music_manager(self) -> Mock:

        return Mock(clear_all_queues = AsyncMock())

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_clear_command_registers_clear_function(self) -> None:

        self.assertIsNotNone(
            self.clear_command,
            _color_error_message_in_red(
                'The "register_clear_command()" function should have registered the "clear" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_clear_returns_early_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.Clear.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            await self.clear_command(context)

        self.assertEqual(
            context.send.call_count,
            0,
            _color_error_message_in_red(
                'No Discord message should be sent when connect_to_voice_channel() returns False.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_clear_stops_playback_when_playing(self) -> None:

        context      = self._build_context(is_playing = True)
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Clear.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Clear.get_music_manager", return_value = mock_manager),
            patch("Commands.Clear.print")
        ):
            await Commands.Clear.clear(context)

        context.voice_client.stop.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_clear_stops_playback_when_paused(self) -> None:

        context      = self._build_context(is_paused = True)
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Clear.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Clear.get_music_manager", return_value = mock_manager),
            patch("Commands.Clear.print")
        ):
            await Commands.Clear.clear(context)

        context.voice_client.stop.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_clear_clears_all_queues(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Clear.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Clear.get_music_manager", return_value = mock_manager),
            patch("Commands.Clear.print")
        ):
            await Commands.Clear.clear(context)

        mock_manager.clear_all_queues.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_clear_sends_feedback_by_default(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Clear.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Clear.get_music_manager", return_value = mock_manager),
            patch("Commands.Clear.print")
        ):
            await Commands.Clear.clear(context)

    #######################################################################################################################
    #######################################################################################################################

    async def test_clear_does_not_send_feedback_when_disabled(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Clear.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Clear.get_music_manager", return_value = mock_manager)
        ):
            await Commands.Clear.clear(context, send_feedback = False)

        self.assertEqual(
            context.send.call_count,
            0,
            _color_error_message_in_red(
                'No Discord message should be sent when send_feedback is False.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
