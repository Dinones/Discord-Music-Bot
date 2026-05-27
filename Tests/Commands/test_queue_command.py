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

import Commands.Queue
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

class Test_Register_Queue_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Queue.register_queue_command(self.bot)
        self.queue_command = self.bot.registered_commands.get("queue")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        context = Mock(
            send   = AsyncMock(),
            author = Mock()
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_queue_command_registers_queue_function(self) -> None:

        self.assertIsNotNone(
            self.queue_command,
            _color_error_message_in_red(
                'The "register_queue_command()" function should have registered the "queue" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_queue_sends_plain_message_when_queue_is_empty(self) -> None:

        context      = self._build_context()
        mock_manager = AsyncMock(
            get_full_queue_snapshot = AsyncMock(return_value = (None, [], []))
        )

        with patch("Commands.Queue.get_music_manager", return_value = mock_manager):
            await Commands.Queue.queue(context)

        context.send.assert_called_once()
        args, kwargs = context.send.call_args
        self.assertNotIn(
            "embed",
            kwargs,
            _color_error_message_in_red(
                'queue() should send a plain text message, not an embed, when the queue is empty.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_queue_calls_get_full_queue_snapshot(self) -> None:

        context      = self._build_context()
        mock_manager = AsyncMock(
            get_full_queue_snapshot = AsyncMock(return_value = ({"title": "Song"}, [], []))
        )

        with (
            patch("Commands.Queue.get_music_manager", return_value = mock_manager),
            patch("Commands.Queue.build_queue_embed", return_value = Mock())
        ):
            await Commands.Queue.queue(context)

        mock_manager.get_full_queue_snapshot.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_queue_sends_embed_to_context(self) -> None:

        context      = self._build_context()
        fake_embed   = Mock()
        mock_manager = AsyncMock(
            get_full_queue_snapshot = AsyncMock(return_value = ({"title": "Song"}, [], []))
        )

        with (
            patch("Commands.Queue.get_music_manager", return_value = mock_manager),
            patch("Commands.Queue.build_queue_embed", return_value = fake_embed)
        ):
            await Commands.Queue.queue(context)

        context.send.assert_called_once_with(embed = fake_embed)

    #######################################################################################################################
    #######################################################################################################################

    async def test_queue_passes_snapshot_data_to_build_queue_embed(self) -> None:

        context       = self._build_context()
        current_song  = {"title": "Now Playing"}
        priority_list = [{"title": "Next Up"}]
        normal_list   = [{"title": "In Queue"}]
        mock_manager  = AsyncMock(
            get_full_queue_snapshot = AsyncMock(return_value = (current_song, priority_list, normal_list))
        )

        with (
            patch("Commands.Queue.get_music_manager", return_value = mock_manager),
            patch("Commands.Queue.build_queue_embed", return_value = Mock()) as mock_build
        ):
            await Commands.Queue.queue(context)

        mock_build.assert_called_once_with(current_song, priority_list, normal_list)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
