###########################################################################################################################
#   Tests for the !resume Discord bot command.                                                                           #
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

import Commands.Resume
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

class Test_Register_Resume_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Resume.register_resume_command(self.bot)
        self.resume_command = self.bot.registered_commands.get("resume")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        context = Mock(
            send         = AsyncMock(),
            guild        = Mock(),
            author       = Mock(),
            voice_client = Mock(
                is_paused = Mock(return_value = True),
                resume    = Mock()
            )
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_resume_command_registers_resume_function(self) -> None:

        self.assertIsNotNone(
            self.resume_command,
            _color_error_message_in_red(
                'The "register_resume_command()" function should have registered the "resume" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_resume_returns_early_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.Resume.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            await self.resume_command(context)

        self.assertEqual(
            context.send.call_count,
            0,
            _color_error_message_in_red(
                'No Discord message should be sent when connect_to_voice_channel() returns False.'
            )
        )
        context.voice_client.resume.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_resume_sends_error_when_not_paused(self) -> None:

        context = self._build_context()
        context.voice_client.is_paused.return_value = False

        with (
            patch("Commands.Resume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Resume.print")
        ):
            await self.resume_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when playback is not paused.'
            )
        )
        context.voice_client.resume.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_resume_resumes_playback_and_sends_confirmation(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Resume.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Resume.print")
        ):
            await self.resume_command(context)

        context.voice_client.resume.assert_called_once()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
