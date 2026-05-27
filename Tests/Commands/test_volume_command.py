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
from typing import Any, Callable
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Commands.Volume
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

class Test_Register_Volume_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Volume.register_volume_command(self.bot)
        self.volume_command = self.bot.registered_commands.get("volume")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self, is_playing: bool = True, is_paused: bool = False) -> Mock:

        context = Mock(
            send         = AsyncMock(),
            guild        = Mock(),
            author       = Mock(),
            voice_client = Mock(
                is_playing = Mock(return_value = is_playing),
                is_paused  = Mock(return_value = is_paused),
                source     = Mock(volume = 1.0)
            )
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_volume_command_registers_volume_function(self) -> None:

        self.assertIsNotNone(
            self.volume_command,
            _color_error_message_in_red(
                'The "register_volume_command()" function should have registered the "volume" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_returns_early_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            await self.volume_command(context)

        self.assertEqual(
            context.send.call_count,
            0,
            _color_error_message_in_red(
                'No Discord message should be sent when connect_to_voice_channel() returns False.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_sends_error_when_argument_is_not_a_number(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Volume.print")
        ):
            await self.volume_command(context, args = "abc")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when the volume argument is not a number.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_sends_error_when_argument_is_out_of_range(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Volume.print")
        ):
            await self.volume_command(context, args = "101")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when the volume argument is out of the 0-100 range.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_sends_error_when_not_playing_and_not_paused(self) -> None:

        context = self._build_context(is_playing = False, is_paused = False)

        with (
            patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Volume.print")
        ):
            await self.volume_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when the bot is not playing or paused.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_reports_current_volume_when_no_argument_given(self) -> None:

        context = self._build_context()
        context.voice_client.source.volume = 1.0

        with (
            patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Volume.print")
        ):
            await self.volume_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one message reporting the current volume when no argument is given.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_sets_source_volume_when_valid_argument_given(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Volume.print")
        ):
            await self.volume_command(context, args = "75")

        self.assertAlmostEqual(
            context.voice_client.source.volume,
            1.5,
            places = 5,
            msg    = _color_error_message_in_red(
                'volume 75 should map to source.volume = 1.5 (75 * 2 / 100).'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_does_not_send_message_on_successful_set(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Volume.print")
        ):
            await self.volume_command(context, args = "75")

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_works_when_bot_is_paused(self) -> None:

        context = self._build_context(is_playing = False, is_paused = True)

        with (
            patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Volume.print")
        ):
            await self.volume_command(context, args = "25")

        self.assertAlmostEqual(
            context.voice_client.source.volume,
            0.5,
            places = 5,
            msg    = _color_error_message_in_red(
                'Volume should be adjustable while the bot is paused.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_zero_maps_to_silence(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Volume.print")
        ):
            await self.volume_command(context, args = "0")

        self.assertAlmostEqual(
            context.voice_client.source.volume,
            0.0,
            places = 5,
            msg    = _color_error_message_in_red(
                'Volume 0 should map to source.volume = 0.0 (silence).'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_volume_hundred_maps_to_maximum(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Volume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Volume.print")
        ):
            await self.volume_command(context, args = "100")

        self.assertAlmostEqual(
            context.voice_client.source.volume,
            2.0,
            places = 5,
            msg    = _color_error_message_in_red(
                'Volume 100 should map to source.volume = 2.0 (maximum).'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
