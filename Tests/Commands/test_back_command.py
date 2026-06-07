###########################################################################################################################
#   Tests for the !back Discord bot command.                                                                             #
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

import Commands.Back
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

class Test_Register_Back_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Back.register_back_command(self.bot)
        self.back_command = self.bot.registered_commands.get("back")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self, is_playing: bool = True, is_paused: bool = False) -> Mock:

        context = Mock(
            send    = AsyncMock(),
            guild   = Mock(),
            author  = Mock(),
            message = Mock(),
            bot     = Mock(loop = Mock(create_task = Mock())),
            voice_client = Mock(
                is_playing = Mock(return_value = is_playing),
                is_paused  = Mock(return_value = is_paused),
                stop       = Mock()
            )
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME
        context.guild.voice_client = context.voice_client

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_back_command_registers_back_function(self) -> None:

        self.assertIsNotNone(
            self.back_command,
            _color_error_message_in_red(
                'The "register_back_command()" function should have registered the "back" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_back_returns_early_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.Back.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            await self.back_command(context)

        self.assertEqual(
            context.send.call_count,
            0,
            _color_error_message_in_red(
                'No Discord message should be sent when connect_to_voice_channel() returns False.'
            )
        )
        context.voice_client.stop.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_back_sends_error_when_no_previous_song(self) -> None:

        context = self._build_context()
        mock_manager = AsyncMock(pop_last_played_song = AsyncMock(return_value = None))

        with (
            patch("Commands.Back.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Back.get_music_manager",        return_value = mock_manager),
            patch("Commands.Back.print")
        ):
            await self.back_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when there is no previous song in history.'
            )
        )
        context.voice_client.stop.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_back_stops_playback_and_sends_reaction_when_playing(self) -> None:

        context      = self._build_context(is_playing = True)
        previous     = {"title": "Previous Song"}
        current      = {"title": "Current Song"}
        mock_manager = AsyncMock(
            pop_last_played_song  = AsyncMock(return_value = previous),
            prepare_back_playback = AsyncMock()
        )
        mock_manager.current_song = current

        with (
            patch("Commands.Back.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Back.get_music_manager",        return_value = mock_manager),
            patch("Commands.Back.send_reaction",            new = AsyncMock(return_value = True)) as mock_reaction,
            patch("Commands.Back.print")
        ):
            await self.back_command(context)

        mock_manager.prepare_back_playback.assert_called_once_with(previous, current)
        context.voice_client.stop.assert_called_once()
        mock_reaction.assert_called_once_with(context.message, "✅")

    #######################################################################################################################
    #######################################################################################################################

    async def test_back_stops_playback_and_sends_reaction_when_paused(self) -> None:

        context      = self._build_context(is_playing = False, is_paused = True)
        previous     = {"title": "Previous Song"}
        current      = {"title": "Current Song"}
        mock_manager = AsyncMock(
            pop_last_played_song  = AsyncMock(return_value = previous),
            prepare_back_playback = AsyncMock()
        )
        mock_manager.current_song = current

        with (
            patch("Commands.Back.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Back.get_music_manager",        return_value = mock_manager),
            patch("Commands.Back.send_reaction",            new = AsyncMock(return_value = True)) as mock_reaction,
            patch("Commands.Back.print")
        ):
            await self.back_command(context)

        mock_manager.prepare_back_playback.assert_called_once_with(previous, current)
        context.voice_client.stop.assert_called_once()
        mock_reaction.assert_called_once_with(context.message, "✅")

    #######################################################################################################################
    #######################################################################################################################

    async def test_back_starts_worker_when_not_playing(self) -> None:

        context      = self._build_context(is_playing = False, is_paused = False)
        previous     = {"title": "Previous Song"}
        mock_manager = AsyncMock(
            pop_last_played_song  = AsyncMock(return_value = previous),
            prepare_back_playback = AsyncMock(),
            reserve_processing    = AsyncMock(return_value = True)
        )
        mock_manager.current_song = None

        with (
            patch("Commands.Back.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Back.get_music_manager",        return_value = mock_manager),
            patch("Commands.Back.send_reaction",            new = AsyncMock(return_value = True)),
            patch("Commands.Back.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.Back.print")
        ):
            await self.back_command(context)

        mock_manager.prepare_back_playback.assert_called_once_with(previous, None)
        context.voice_client.stop.assert_not_called()
        mock_manager.reserve_processing.assert_called_once()
        context.bot.loop.create_task.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_back_does_not_start_worker_when_already_processing(self) -> None:

        context      = self._build_context(is_playing = False, is_paused = False)
        previous     = {"title": "Previous Song"}
        mock_manager = AsyncMock(
            pop_last_played_song  = AsyncMock(return_value = previous),
            prepare_back_playback = AsyncMock(),
            reserve_processing    = AsyncMock(return_value = False)
        )
        mock_manager.current_song = None

        with (
            patch("Commands.Back.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Back.get_music_manager",        return_value = mock_manager),
            patch("Commands.Back.send_reaction",            new = AsyncMock(return_value = True)),
            patch("Commands.Back.print")
        ):
            await self.back_command(context)

        context.bot.loop.create_task.assert_not_called()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
