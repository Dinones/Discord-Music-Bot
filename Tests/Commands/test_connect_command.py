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

import Commands.Connect
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

class Test_Register_Connect_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        """
        Build a fake bot and capture the registered connect command callback for each test.
        """

        self.bot = _Fake_Bot()
        Commands.Connect.register_connect_command(self.bot)
        self.connect_command = self.bot.registered_commands.get("connect")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        """
        Create a default command context with guild, author and voice channel mocks.

        Returns:
            Mock: Baseline mocked command context.
        """

        context = Mock(
            send   = AsyncMock(),
            guild  = Mock(),
            author = Mock(
                voice = Mock(
                    channel = Mock(
                        connect = AsyncMock()
                    )
                )
            )
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME

        context.voice_client = None
        context.author.voice.channel.name = "General"

        return context

    #######################################################################################################################
    #######################################################################################################################
    
    def _expand_voice_client(self, context) -> None:

        """
        Add a mocked voice client to an existing context to simulate connected bot state.
        """

        context.voice_client = Mock(
            move_to = AsyncMock()
        )

        context.voice_client.channel = context.author.voice.channel

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_connect_command_registers_connect_function(self) -> None:

        """
        Test that register_connect_command() registers a "connect" command in the bot.
        """

        self.assertIsNotNone(
            self.connect_command,
            _color_error_message_in_red(
                'The "register_connect_command()" function should have registered the "connect" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_connect_sends_dm_error_when_user_is_sending_private_message(self) -> None:

        """
        Test that connect() sends an error message when the user invokes the command from DM.
        """

        context = self._build_context()
        context.guild = None

        with patch("Commands.Connect.print") as mock_print:
            await self.connect_command(context)

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

    async def test_connect_sends_error_when_user_is_not_connected_to_voice_channel(self) -> None:

        """
        Test that connect() sends an error message when the user is not connected to a voice channel.
        """

        context = self._build_context()
        context.author.voice = None

        with patch("Commands.Connect.print") as mock_print:
            await self.connect_command(context)

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

    async def test_connect_moves_to_user_channel_when_bot_is_already_connected_to_different_channel(self) -> None:

        """
        Test that connect() moves the bot to the user's voice channel when the bot is already connected elsewhere.
        """

        context = self._build_context()
        self._expand_voice_client(context)
        context.voice_client.channel = Mock()
        context.voice_client.channel.name = "Channel_2"

        await self.connect_command(context)

        context.voice_client.move_to.assert_called_once_with(context.author.voice.channel)

        self.assertEqual(
            context.author.voice.channel.connect.call_count,
            0,
            _color_error_message_in_red(
                f'The "voice_channel.connect()" function should not have been called when moving channels.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_connect_does_nothing_when_bot_is_already_in_user_channel(self) -> None:

        """
        Test that connect() exits without reconnecting when the bot is already in the user's voice channel.
        """

        context = self._build_context()
        self._expand_voice_client(context)

        await self.connect_command(context)

        self.assertEqual(
            context.voice_client.move_to.call_count,
            0,
            _color_error_message_in_red(
                f'The "voice_client.move_to()" function should not have been called when already in the same channel.'
            )
        )

        self.assertEqual(
            context.author.voice.channel.connect.call_count,
            0,
            _color_error_message_in_red(
                f'The "voice_channel.connect()" function should not have been called when already in the same channel.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_connect_joins_user_voice_channel_when_bot_is_not_connected(self) -> None:

        """
        Test that connect() joins the user's voice channel when the bot is not connected.
        """

        context = self._build_context()

        await self.connect_command(context)

        self.assertEqual(
            context.author.voice.channel.connect.call_count,
            1,
            _color_error_message_in_red(
                f'The "voice_channel.connect()" function should have been called exactly "1" time instead of ' +
                f'"{context.author.voice.channel.connect.call_count}".'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
