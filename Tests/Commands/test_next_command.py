###########################################################################################################################
#   Tests for the !next and !skip Discord bot commands.                                                                  #
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

import Commands.Next
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

class Test_Register_Next_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Next.register_next_command(self.bot)
        self.next_command = self.bot.registered_commands.get("next")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self, is_playing: bool = True, is_paused: bool = False) -> Mock:

        context = Mock(
            send    = AsyncMock(),
            guild   = Mock(),
            author  = Mock(),
            message = Mock(),
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

    async def test_register_next_command_registers_next_function(self) -> None:

        self.assertIsNotNone(
            self.next_command,
            _color_error_message_in_red(
                'The "register_next_command()" function should have registered the "next" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_next_returns_early_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.Next.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            await self.next_command(context)

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

    async def test_next_sends_error_when_nothing_is_playing_or_paused(self) -> None:

        context = self._build_context(is_playing = False, is_paused = False)

        with (
            patch("Commands.Next.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Next.print")
        ):
            await self.next_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when the bot is not playing anything.'
            )
        )
        context.voice_client.stop.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_next_stops_playback_and_sends_reaction_when_playing(self) -> None:

        context = self._build_context(is_playing = True)

        with (
            patch("Commands.Next.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Next.send_reaction",            new = AsyncMock(return_value = True)) as mock_reaction,
            patch("Commands.Next.print")
        ):
            await self.next_command(context)

        context.voice_client.stop.assert_called_once()
        mock_reaction.assert_called_once_with(context.message, "✅")

    #######################################################################################################################
    #######################################################################################################################

    async def test_next_stops_playback_and_sends_reaction_when_paused(self) -> None:

        context = self._build_context(is_playing = False, is_paused = True)

        with (
            patch("Commands.Next.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Next.send_reaction",            new = AsyncMock(return_value = True)) as mock_reaction,
            patch("Commands.Next.print")
        ):
            await self.next_command(context)

        context.voice_client.stop.assert_called_once()
        mock_reaction.assert_called_once_with(context.message, "✅")

    #######################################################################################################################
    #######################################################################################################################

    async def test_skip_count_drops_extra_songs_before_stopping(self) -> None:

        context       = self._build_context(is_playing = True)
        mock_manager  = Mock(drop_songs = AsyncMock())

        with (
            patch("Commands.Next.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Next.send_reaction",            new = AsyncMock(return_value = True)),
            patch("Commands.Next.get_music_manager",        return_value = mock_manager),
            patch("Commands.Next.print")
        ):
            await self.next_command(context, "4")

        mock_manager.drop_songs.assert_called_once_with(3)
        context.voice_client.stop.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_skip_count_1_does_not_call_drop_songs(self) -> None:

        context      = self._build_context(is_playing = True)
        mock_manager = Mock(drop_songs = AsyncMock())

        with (
            patch("Commands.Next.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Next.send_reaction",            new = AsyncMock(return_value = True)),
            patch("Commands.Next.get_music_manager",        return_value = mock_manager),
            patch("Commands.Next.print")
        ):
            await self.next_command(context, "1")

        mock_manager.drop_songs.assert_not_called()
        context.voice_client.stop.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_skip_invalid_count_defaults_to_1(self) -> None:

        context      = self._build_context(is_playing = True)
        mock_manager = Mock(drop_songs = AsyncMock())

        with (
            patch("Commands.Next.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Next.send_reaction",            new = AsyncMock(return_value = True)),
            patch("Commands.Next.get_music_manager",        return_value = mock_manager),
            patch("Commands.Next.print")
        ):
            await self.next_command(context, "abc")

        mock_manager.drop_songs.assert_not_called()
        context.voice_client.stop.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_skip_count_capped_at_max_songs_and_sends_message(self) -> None:

        context      = self._build_context(is_playing = True)
        mock_manager = Mock(drop_songs = AsyncMock())

        with (
            patch("Commands.Next.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Next.send_reaction",            new = AsyncMock(return_value = True)),
            patch("Commands.Next.get_music_manager",        return_value = mock_manager),
            patch("Commands.Next._MAX_SONGS",               new = 5),
            patch("Commands.Next.print")
        ):
            await self.next_command(context, "999")

        mock_manager.drop_songs.assert_called_once_with(4)
        context.send.assert_called_once()
        context.voice_client.stop.assert_called_once()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
