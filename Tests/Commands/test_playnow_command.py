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

import Commands.PlayNow
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

class Test_Register_PlayNow_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.PlayNow.register_playnow_command(self.bot)
        self.playnow_command = self.bot.registered_commands.get("playnow")

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
                is_paused  = Mock(return_value = is_paused)
            )
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME
        context.guild.voice_client = context.voice_client

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_playnow_command_registers_playnow_function(self) -> None:

        self.assertIsNotNone(
            self.playnow_command,
            _color_error_message_in_red(
                'The "register_playnow_command()" function should have registered the "playnow" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnow_calls_playnext_with_priority_front_true(self) -> None:

        context = self._build_context()

        with patch("Commands.PlayNow.playnext", new = AsyncMock(return_value = False)) as mock_playnext:
            await self.playnow_command(context, args = "some song")

        mock_playnext.assert_called_once_with(context, "some song", priority_front = True)

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnow_calls_skip_when_single_song_and_playing(self) -> None:

        context = self._build_context(is_playing = True)

        with (
            patch("Commands.PlayNow.playnext", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNow.skip",     new = AsyncMock()) as mock_skip
        ):
            await self.playnow_command(context, args = "some song")

        mock_skip.assert_called_once_with(context)

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnow_calls_skip_when_single_song_and_paused(self) -> None:

        context = self._build_context(is_playing = False, is_paused = True)

        with (
            patch("Commands.PlayNow.playnext", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNow.skip",     new = AsyncMock()) as mock_skip
        ):
            await self.playnow_command(context, args = "some song")

        mock_skip.assert_called_once_with(context)

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnow_does_not_call_skip_when_not_playing(self) -> None:

        context = self._build_context(is_playing = False, is_paused = False)

        with (
            patch("Commands.PlayNow.playnext", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNow.skip",     new = AsyncMock()) as mock_skip
        ):
            await self.playnow_command(context, args = "some song")

        mock_skip.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnow_does_not_call_skip_when_playlist(self) -> None:

        context = self._build_context(is_playing = True)

        with (
            patch("Commands.PlayNow.playnext", new = AsyncMock(return_value = False)),
            patch("Commands.PlayNow.skip",     new = AsyncMock()) as mock_skip
        ):
            await self.playnow_command(context, args = "some playlist url")

        mock_skip.assert_not_called()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
