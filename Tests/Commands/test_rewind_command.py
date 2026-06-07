###########################################################################################################################
#   Tests for the !rewind Discord bot command.                                                                           #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from typing import Any, Callable
from unittest.mock import Mock, AsyncMock, MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Commands.Rewind
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

class Test_Register_Rewind_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Rewind.register_rewind_command(self.bot)
        self.rewind_command = self.bot.registered_commands.get("rewind")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self, is_playing: bool = True, is_paused: bool = False) -> Mock:

        voice_client = Mock(
            is_playing = Mock(return_value = is_playing),
            is_paused  = Mock(return_value = is_paused),
            stop       = Mock()
        )

        context              = Mock(send = AsyncMock())
        context.author       = Mock()
        context.author.name  = CONST.TESTING_AUTHOR_NAME
        context.guild        = Mock(voice_client = voice_client)
        context.voice_client = voice_client

        return context

    #######################################################################################################################
    #######################################################################################################################

    def _build_music_manager(self, current_song: dict = None, elapsed: float = 60.0) -> Mock:

        updater                    = Mock()
        updater._play_start_time   = 0.0
        updater._paused_acc        = 0.0
        updater._seek_offset       = 0

        manager                 = Mock()
        manager.current_song    = current_song or {"title": "Test Song", "duration": 300}
        manager.current_updater = updater
        manager.prepare_rewind_playback = AsyncMock()

        return manager

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_rewind_command_registers_rewind_function(self) -> None:

        self.assertIsNotNone(
            self.rewind_command,
            _color_error_message_in_red(
                'The "register_rewind_command()" function should have registered the "rewind" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_rewind_returns_early_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.Rewind.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            await self.rewind_command(context, args = "30")

        self.assertEqual(
            context.send.call_count,
            0,
            _color_error_message_in_red(
                'No Discord message should be sent when connect_to_voice_channel() returns False.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_rewind_sends_error_when_argument_is_not_a_number(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Rewind.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Rewind.print")
        ):
            await self.rewind_command(context, args = "abc")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when the rewind argument is not a number.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_rewind_sends_error_when_argument_is_zero(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Rewind.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Rewind.print")
        ):
            await self.rewind_command(context, args = "0")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when the rewind argument is zero.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_rewind_sends_error_when_not_playing_and_not_paused(self) -> None:

        context = self._build_context(is_playing = False, is_paused = False)

        with (
            patch("Commands.Rewind.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Rewind.get_music_manager", return_value = self._build_music_manager()),
            patch("Commands.Rewind.print")
        ):
            await self.rewind_command(context, args = "30")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when bot is not playing or paused.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_rewind_calls_voice_client_stop_on_success(self) -> None:

        context = self._build_context()
        manager = self._build_music_manager()

        with (
            patch("Commands.Rewind.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Rewind.get_music_manager", return_value = manager),
            patch("Commands.Rewind.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Rewind.print")
        ):
            await self.rewind_command(context, args = "30")

        context.guild.voice_client.stop.assert_called_once()

        self.assertEqual(
            context.guild.voice_client.stop.call_count,
            1,
            _color_error_message_in_red(
                'rewind() should call voice_client.stop() exactly once to trigger the queue worker.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_rewind_seek_offset_is_elapsed_minus_rewind_seconds(self) -> None:

        context = self._build_context()
        manager = self._build_music_manager()
        # Updater says song started at t=0, no pausing; loop.time() returns 60 → elapsed = 60s
        manager.current_updater._play_start_time = 0.0
        manager.current_updater._paused_acc      = 0.0

        with (
            patch("Commands.Rewind.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Rewind.get_music_manager", return_value = manager),
            patch("Commands.Rewind.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Rewind.print")
        ):
            await self.rewind_command(context, args = "20")

        called_song = manager.prepare_rewind_playback.call_args[0][0]

        self.assertEqual(
            called_song.get("seek_offset"),
            40,
            _color_error_message_in_red(
                'With 60s elapsed and rewind=20, seek_offset should be 40.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_rewind_seek_offset_is_zero_when_rewind_exceeds_elapsed(self) -> None:

        context = self._build_context()
        manager = self._build_music_manager()
        manager.current_updater._play_start_time = 0.0
        manager.current_updater._paused_acc      = 0.0

        with (
            patch("Commands.Rewind.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Rewind.get_music_manager", return_value = manager),
            patch("Commands.Rewind.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 10.0))),
            patch("Commands.Rewind.print")
        ):
            await self.rewind_command(context, args = "30")

        called_song = manager.prepare_rewind_playback.call_args[0][0]

        self.assertEqual(
            called_song.get("seek_offset"),
            0,
            _color_error_message_in_red(
                'When rewind seconds exceed elapsed time, seek_offset should be 0 (restart from beginning).'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_rewind_subtracts_paused_time_from_elapsed(self) -> None:

        context = self._build_context()
        manager = self._build_music_manager()
        # Song started at t=0, 15s was spent paused, loop.time()=60 → real elapsed = 45s
        manager.current_updater._play_start_time = 0.0
        manager.current_updater._paused_acc      = 15.0

        with (
            patch("Commands.Rewind.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Rewind.get_music_manager", return_value = manager),
            patch("Commands.Rewind.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Rewind.print")
        ):
            await self.rewind_command(context, args = "10")

        called_song = manager.prepare_rewind_playback.call_args[0][0]

        self.assertEqual(
            called_song.get("seek_offset"),
            35,
            _color_error_message_in_red(
                'Elapsed should account for paused time: (60 - 0 - 15) - 10 = 35.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_rewind_works_while_paused(self) -> None:

        context = self._build_context(is_playing = False, is_paused = True)
        manager = self._build_music_manager()

        with (
            patch("Commands.Rewind.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Rewind.get_music_manager", return_value = manager),
            patch("Commands.Rewind.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Rewind.print")
        ):
            await self.rewind_command(context, args = "10")

        context.guild.voice_client.stop.assert_called_once()

        self.assertEqual(
            context.guild.voice_client.stop.call_count,
            1,
            _color_error_message_in_red(
                'rewind() should work while paused, calling voice_client.stop() once.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
