###########################################################################################################################
#   Tests for the !seek Discord bot command.                                                                              #
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

import Commands.Seek
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

class Test_Parse_Seek_Arg(unittest.TestCase):

    def test_plain_integer_returns_seconds(self) -> None:

        self.assertEqual(
            Commands.Seek._parse_seek_arg("90"),
            90,
            _color_error_message_in_red("Plain integer '90' should parse to 90 seconds.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_zero_is_valid(self) -> None:

        self.assertEqual(
            Commands.Seek._parse_seek_arg("0"),
            0,
            _color_error_message_in_red("'0' should be valid and return 0.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_mm_ss_format_returns_total_seconds(self) -> None:

        self.assertEqual(
            Commands.Seek._parse_seek_arg("1:30"),
            90,
            _color_error_message_in_red("'1:30' should parse to 90 seconds.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_mm_ss_with_zero_minutes(self) -> None:

        self.assertEqual(
            Commands.Seek._parse_seek_arg("0:45"),
            45,
            _color_error_message_in_red("'0:45' should parse to 45 seconds.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_invalid_string_returns_none(self) -> None:

        self.assertIsNone(
            Commands.Seek._parse_seek_arg("abc"),
            _color_error_message_in_red("Non-numeric string should return None.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_invalid_mm_ss_with_non_digits_returns_none(self) -> None:

        self.assertIsNone(
            Commands.Seek._parse_seek_arg("1:xx"),
            _color_error_message_in_red("MM:SS with non-digit seconds should return None.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_negative_number_returns_none(self) -> None:

        self.assertIsNone(
            Commands.Seek._parse_seek_arg("-5"),
            _color_error_message_in_red("Negative number should return None.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_empty_string_returns_none(self) -> None:

        self.assertIsNone(
            Commands.Seek._parse_seek_arg(""),
            _color_error_message_in_red("Empty string should return None.")
        )

###########################################################################################################################
###########################################################################################################################

class Test_Register_Seek_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Seek.register_seek_command(self.bot)
        self.seek_command = self.bot.registered_commands.get("seek")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self, is_playing: bool = True, is_paused: bool = False) -> Mock:

        voice_client = Mock(
            is_playing = Mock(return_value = is_playing),
            is_paused  = Mock(return_value = is_paused),
            stop       = Mock()
        )

        context             = Mock(send = AsyncMock())
        context.author      = Mock()
        context.author.name = CONST.TESTING_AUTHOR_NAME
        context.guild       = Mock(voice_client = voice_client)
        context.voice_client = voice_client

        return context

    #######################################################################################################################
    #######################################################################################################################

    def _build_music_manager(self, duration: int = 300) -> Mock:

        manager                          = Mock()
        manager.current_song             = {"title": "Test Song", "duration": duration}
        manager.current_updater          = Mock()
        manager.prepare_rewind_playback  = AsyncMock()

        return manager

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_seek_command_registers_seek_function(self) -> None:

        self.assertIsNotNone(
            self.seek_command,
            _color_error_message_in_red(
                'register_seek_command() should have registered the "seek" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_returns_early_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.Seek.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            await self.seek_command(context, args = "60")

        self.assertEqual(
            context.send.call_count,
            0,
            _color_error_message_in_red(
                'No Discord message should be sent when connect_to_voice_channel() returns False.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_sends_error_when_argument_is_invalid(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Seek.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Seek.print")
        ):
            await self.seek_command(context, args = "abc")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when the seek argument is invalid.'
            )
        )
        context.guild.voice_client.stop.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_sends_error_when_not_playing_and_not_paused(self) -> None:

        context = self._build_context(is_playing = False, is_paused = False)

        with (
            patch("Commands.Seek.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Seek.get_music_manager", return_value = self._build_music_manager()),
            patch("Commands.Seek.print")
        ):
            await self.seek_command(context, args = "60")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when bot is not playing or paused.'
            )
        )
        context.guild.voice_client.stop.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_uses_correct_offset_for_plain_seconds(self) -> None:

        context = self._build_context()
        manager = self._build_music_manager()

        with (
            patch("Commands.Seek.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Seek.get_music_manager", return_value = manager),
            patch("Commands.Seek.print")
        ):
            await self.seek_command(context, args = "90")

        called_song = manager.prepare_rewind_playback.call_args[0][0]

        self.assertEqual(
            called_song.get("seek_offset"),
            90,
            _color_error_message_in_red("seek_offset should be 90 when argument is '90'.")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_uses_correct_offset_for_mm_ss(self) -> None:

        context = self._build_context()
        manager = self._build_music_manager()

        with (
            patch("Commands.Seek.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Seek.get_music_manager", return_value = manager),
            patch("Commands.Seek.print")
        ):
            await self.seek_command(context, args = "1:30")

        called_song = manager.prepare_rewind_playback.call_args[0][0]

        self.assertEqual(
            called_song.get("seek_offset"),
            90,
            _color_error_message_in_red("seek_offset should be 90 when argument is '1:30'.")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_zero_restarts_song_from_beginning(self) -> None:

        context = self._build_context()
        manager = self._build_music_manager()

        with (
            patch("Commands.Seek.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Seek.get_music_manager", return_value = manager),
            patch("Commands.Seek.print")
        ):
            await self.seek_command(context, args = "0")

        called_song = manager.prepare_rewind_playback.call_args[0][0]

        self.assertEqual(
            called_song.get("seek_offset"),
            0,
            _color_error_message_in_red("seek_offset should be 0 when argument is '0'.")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_clamps_to_duration_when_exceeding_song_length(self) -> None:

        context = self._build_context()
        manager = self._build_music_manager(duration = 120)

        with (
            patch("Commands.Seek.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Seek.get_music_manager", return_value = manager),
            patch("Commands.Seek.print")
        ):
            await self.seek_command(context, args = "999")

        called_song = manager.prepare_rewind_playback.call_args[0][0]

        self.assertEqual(
            called_song.get("seek_offset"),
            120,
            _color_error_message_in_red("seek_offset should be clamped to the song duration (120s).")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_calls_voice_client_stop_on_success(self) -> None:

        context = self._build_context()
        manager = self._build_music_manager()

        with (
            patch("Commands.Seek.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Seek.get_music_manager", return_value = manager),
            patch("Commands.Seek.print")
        ):
            await self.seek_command(context, args = "60")

        context.guild.voice_client.stop.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_works_while_paused(self) -> None:

        context = self._build_context(is_playing = False, is_paused = True)
        manager = self._build_music_manager()

        with (
            patch("Commands.Seek.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Seek.get_music_manager", return_value = manager),
            patch("Commands.Seek.print")
        ):
            await self.seek_command(context, args = "45")

        context.guild.voice_client.stop.assert_called_once()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
