###########################################################################################################################
#   Tests for the !restart Discord bot command.                                                                           #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import asyncio
import os
import sys
import unittest
from typing import Any, Callable
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Commands.Restart
import Utils.Constants as CONST
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class _Fake_Bot:

    def __init__(self) -> None:
        self.registered_commands = {}
        self.close               = AsyncMock()
        self.wait_for            = AsyncMock(return_value = (Mock(), Mock()))

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

class Test_Register_Restart_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Restart.register_restart_command(self.bot)
        self.restart_command = self.bot.registered_commands.get("restart")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        confirm_msg         = Mock(id = 999)
        confirm_msg.add_reaction = AsyncMock()

        context             = Mock()
        context.send        = AsyncMock(return_value = confirm_msg)
        context.author      = Mock()
        context.author.name = CONST.TESTING_AUTHOR_NAME
        context.bot         = self.bot

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_restart_command_registers_restart_function(self) -> None:

        self.assertIsNotNone(
            self.restart_command,
            _color_error_message_in_red(
                'register_restart_command() should have registered the "restart" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_restart_sends_confirmation_message(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Restart.send_reaction", new = AsyncMock()),
            patch("Commands.Restart.subprocess.Popen"),
            patch("Commands.Restart.os._exit"),
            patch("Commands.Restart.print")
        ):
            await self.restart_command(context)

        self.assertGreaterEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red("restart() should send at least one message.")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_restart_adds_skull_reaction_to_confirmation_message(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Restart.send_reaction", new = AsyncMock()) as mock_reaction,
            patch("Commands.Restart.subprocess.Popen"),
            patch("Commands.Restart.os._exit"),
            patch("Commands.Restart.print")
        ):
            await self.restart_command(context)

        mock_reaction.assert_called_once_with(context.send.return_value, "💀")

    #######################################################################################################################
    #######################################################################################################################

    async def test_restart_waits_for_skull_reaction(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Restart.send_reaction", new = AsyncMock()),
            patch("Commands.Restart.subprocess.Popen"),
            patch("Commands.Restart.os._exit"),
            patch("Commands.Restart.print")
        ):
            await self.restart_command(context)

        self.bot.wait_for.assert_called_once()
        event_name = self.bot.wait_for.call_args[0][0]

        self.assertEqual(
            event_name,
            "reaction_add",
            _color_error_message_in_red('restart() should wait for a "reaction_add" event.')
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_restart_proceeds_after_skull_confirmation(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Restart.send_reaction", new = AsyncMock()),
            patch("Commands.Restart.subprocess.Popen"),
            patch("Commands.Restart.os._exit") as mock_exit,
            patch("Commands.Restart.print")
        ):
            await self.restart_command(context)
            mock_exit.assert_called_once_with(0)

    #######################################################################################################################
    #######################################################################################################################

    async def test_restart_closes_bot_before_exec_on_confirmation(self) -> None:

        context  = self._build_context()
        call_log = []

        async def track_close() -> None:
            call_log.append("close")

        context.bot.close    = track_close
        context.bot.wait_for = AsyncMock(return_value = (Mock(), Mock()))

        with (
            patch("Commands.Restart.send_reaction", new = AsyncMock()),
            patch("Commands.Restart.subprocess.Popen", side_effect = lambda *_: call_log.append("popen")),
            patch("Commands.Restart.os._exit"),
            patch("Commands.Restart.print")
        ):
            await self.restart_command(context)

        self.assertEqual(
            call_log,
            ["close", "popen"],
            _color_error_message_in_red("bot.close() must complete before subprocess.Popen() is called.")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_restart_cancelled_on_timeout(self) -> None:

        context = self._build_context()
        context.bot.wait_for = AsyncMock(side_effect = asyncio.TimeoutError())

        with (
            patch("Commands.Restart.send_reaction", new = AsyncMock()),
            patch("Commands.Restart.subprocess.Popen") as mock_popen,
            patch("Commands.Restart.os._exit"),
            patch("Commands.Restart.print")
        ):
            await self.restart_command(context)

        mock_popen.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_restart_sends_cancelled_message_on_timeout(self) -> None:

        context = self._build_context()
        context.bot.wait_for = AsyncMock(side_effect = asyncio.TimeoutError())

        with (
            patch("Commands.Restart.send_reaction", new = AsyncMock()),
            patch("Commands.Restart.subprocess.Popen"),
            patch("Commands.Restart.os._exit"),
            patch("Commands.Restart.print")
        ):
            await self.restart_command(context)

        sent_texts = [call[0][0] for call in context.send.call_args_list if call[0]]

        self.assertTrue(
            any("cancel" in t.lower() for t in sent_texts),
            _color_error_message_in_red(
                "restart() should send a cancellation message when the confirmation times out."
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
