###########################################################################################################################
#   Tests for the !ping Discord bot command.                                                                             #
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

import Commands.Ping
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

class Test_Register_Ping_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        self.bot.latency = 0.042
        Commands.Ping.register_ping_command(self.bot)
        self.ping_command = self.bot.registered_commands.get("ping")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        context           = Mock(send = AsyncMock())
        context.author    = Mock()
        context.author.name = "testuser"
        context.bot       = self.bot

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_ping_command_registers_ping_function(self) -> None:

        self.assertIsNotNone(
            self.ping_command,
            _color_error_message_in_red(
                'The "register_ping_command()" function should have registered the "ping" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_ping_sends_exactly_one_message(self) -> None:

        context = self._build_context()

        with patch("Commands.Ping.print"):
            await self.ping_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'ping() should send exactly one message.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_ping_message_contains_latency(self) -> None:

        context = self._build_context()

        with patch("Commands.Ping.print"):
            await self.ping_command(context)

        sent_text = context.send.call_args[0][0]

        self.assertIn(
            "42",
            sent_text,
            _color_error_message_in_red(
                'ping() should include the latency value (42 ms for bot.latency=0.042) in the sent message.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_ping_adds_paddle_reaction_to_command_message(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Ping.print"),
            patch("Commands.Ping.send_reaction", new = AsyncMock()) as mock_reaction
        ):
            await self.ping_command(context)

        self.assertEqual(
            mock_reaction.call_args[0][1],
            "🏓",
            _color_error_message_in_red(
                'ping() should call send_reaction with the 🏓 emoji.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_ping_rounds_latency_to_milliseconds(self) -> None:

        context          = self._build_context()
        self.bot.latency = 0.1234

        with patch("Commands.Ping.print"):
            await self.ping_command(context)

        sent_text = context.send.call_args[0][0]

        self.assertIn(
            "123",
            sent_text,
            _color_error_message_in_red(
                'ping() should truncate fractional milliseconds (0.1234 s → 123 ms).'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
