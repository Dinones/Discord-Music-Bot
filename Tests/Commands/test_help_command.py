###########################################################################################################################
#   Tests for the !help Discord bot command.                                                                              #
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

import discord
import Commands.Help
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

class Test_Build_Help_Embed(unittest.TestCase):

    def test_returns_discord_embed(self) -> None:

        embed = Commands.Help.build_help_embed()

        self.assertIsInstance(
            embed,
            discord.Embed,
            _color_error_message_in_red("build_help_embed() should return a discord.Embed.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_has_title(self) -> None:

        embed = Commands.Help.build_help_embed()

        self.assertTrue(
            embed.title,
            _color_error_message_in_red("build_help_embed() should set a non-empty embed title.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_has_all_sections(self) -> None:

        embed  = Commands.Help.build_help_embed()
        fields = embed.fields

        self.assertEqual(
            len(fields),
            len(Commands.Help._SECTIONS),
            _color_error_message_in_red(
                f"build_help_embed() should have {len(Commands.Help._SECTIONS)} fields, one per section."
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_fields_are_not_inline(self) -> None:

        embed = Commands.Help.build_help_embed()

        for field in embed.fields:
            self.assertFalse(
                field.inline,
                _color_error_message_in_red(
                    f'Field "{field.name}" should not be inline so each section spans the full width.'
                )
            )

###########################################################################################################################
###########################################################################################################################

class Test_Register_Help_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Help.register_help_command(self.bot)
        self.help_command = self.bot.registered_commands.get("help")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        context             = Mock(send = AsyncMock())
        context.author      = Mock()
        context.author.name = "testuser"

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_help_command_registers_help_function(self) -> None:

        self.assertIsNotNone(
            self.help_command,
            _color_error_message_in_red(
                'register_help_command() should have registered the "help" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_help_sends_exactly_one_message(self) -> None:

        context = self._build_context()

        with patch("Commands.Help.print"):
            await self.help_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red("help() should send exactly one message.")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_help_sends_embed(self) -> None:

        context = self._build_context()

        with patch("Commands.Help.print"):
            await self.help_command(context)

        kwargs = context.send.call_args.kwargs

        self.assertIsInstance(
            kwargs.get("embed"),
            discord.Embed,
            _color_error_message_in_red("help() should send a discord.Embed.")
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
