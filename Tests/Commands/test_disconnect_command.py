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

import Commands.Disconnect
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

        """
        Mimic discord.py command decorator registration for unit tests.

        Args:
            *args (Any): Positional arguments passed to the command decorator.
            **kwargs (Any): Keyword arguments passed to the command decorator.

        Returns:
            Callable[[Callable[..., Any]], Callable[..., Any]]: A decorator that registers command callbacks.
        """

        def decorator(function: Callable[..., Any]) -> Callable[..., Any]:

            """
            Store a decorated function as a registered command and return it unchanged.

            Args:
                function (Callable[..., Any]): Command callback function.

            Returns:
                Callable[..., Any]: The same callback function after registration.
            """

            command_name = kwargs.get("name", function.__name__)
            self.registered_commands[command_name] = function

            return function

        return decorator

###########################################################################################################################
###########################################################################################################################

class Test_Register_Disconnect_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        """
        Build a fake bot and capture the registered disconnect command callback for each test.
        """

        self.bot = _Fake_Bot()
        Commands.Disconnect.register_disconnect_command(self.bot)
        self.disconnect_command = self.bot.registered_commands.get("disconnect")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        """
        Create a default command context where user and bot share the same voice channel.

        Returns:
            Mock: Baseline mocked command context.
        """

        context = Mock(
            send   = AsyncMock(),
            guild  = Mock(),
            author = Mock(
                voice = Mock(
                    channel = Mock()
                )
            )
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME
        context.author.voice.channel.name = "General"
        context.voice_client = None

        return context

    #######################################################################################################################
    #######################################################################################################################

    def _expand_voice_client(self, context) -> None:

        """
        Add a mocked voice client to an existing context to simulate connected bot state.
        """

        context.voice_client = Mock(
            disconnect = AsyncMock()
        )

        context.voice_client.channel = context.author.voice.channel

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_disconnect_command_registers_disconnect_function(self) -> None:

        """
        Test that register_disconnect_command() registers a "disconnect" command in the bot.
        """

        self.assertIsNotNone(
            self.disconnect_command,
            _color_error_message_in_red(
                'The "register_disconnect_command()" function should have registered the "disconnect" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_disconnect_sends_dm_error_when_user_is_sending_private_message(self) -> None:

        """
        Test that disconnect() sends an error message when the user invokes the command from DM.
        """

        context = self._build_context()
        context.guild = None

        with patch("Commands.Disconnect.print") as mock_print:
            await self.disconnect_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                f'The "context.send()" function should have been called exactly "1" time instead of ' +
                f'"{context.send.call_count}".'
            )
        )

        self.assertEqual(
            mock_print.call_count,
            1,
            _color_error_message_in_red(
                f'Exactly one logging message should have been printed in terminal for DM attempts.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_disconnect_sends_error_when_bot_is_not_connected_to_voice_channel(self) -> None:

        """
        Test that disconnect() sends an error message when the bot is not connected to voice.
        """

        context = self._build_context()

        with patch("Commands.Disconnect.print") as mock_print:
            await self.disconnect_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                f'The "context.send()" function should have been called exactly "1" time instead of ' +
                f'"{context.send.call_count}".'
            )
        )

        self.assertEqual(
            mock_print.call_count,
            1,
            _color_error_message_in_red(
                f'Exactly one logging message should have been printed in terminal when bot is not in VC.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_disconnect_sends_error_when_user_is_not_connected_to_voice_channel(self) -> None:

        """
        Test that disconnect() sends an error message when the user is not connected to voice.
        """

        context = self._build_context()
        context.author.voice = None

        with patch("Commands.Disconnect.print") as mock_print:
            await self.disconnect_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                f'The "context.send()" function should have been called exactly "1" time instead of ' +
                f'"{context.send.call_count}".'
            )
        )

        self.assertEqual(
            mock_print.call_count,
            1,
            _color_error_message_in_red(
                f'Exactly one logging message should have been printed in terminal when user is not in VC.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_disconnect_sends_error_when_user_is_not_in_the_same_bot_voice_channel(self) -> None:

        """
        Test that disconnect() sends an error message when the user is not in the bot's voice channel.
        """

        context = self._build_context()
        self._expand_voice_client(context)
        context.author.voice.channel = Mock()
        context.author.voice.channel.name = "Music-2"

        with patch("Commands.Disconnect.print") as mock_print:
            await self.disconnect_command(context)

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                f'The "context.send()" function should have been called exactly "1" time instead of ' +
                f'"{context.send.call_count}".'
            )
        )

        self.assertEqual(
            mock_print.call_count,
            1,
            _color_error_message_in_red(
                f'Exactly one logging message should have been printed in terminal when user is in a different VC.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_disconnect_disconnects_bot_when_user_is_in_the_same_bot_voice_channel(self) -> None:

        """
        Test that disconnect() disconnects the bot when the user is in the same voice channel.
        """

        context = self._build_context()
        self._expand_voice_client(context)

        await self.disconnect_command(context)

        self.assertEqual(
            context.voice_client.disconnect.call_count,
            1,
            _color_error_message_in_red(
                f'The "voice_client.disconnect()" function should have been called exactly "1" time instead of ' +
                f'"{context.voice_client.disconnect.call_count}".'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
