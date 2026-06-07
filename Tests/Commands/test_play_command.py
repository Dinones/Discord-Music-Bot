###########################################################################################################################
#   Tests for the !play Discord bot command.                                                                             #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from typing import Any, Callable
from unittest.mock import Mock, AsyncMock, patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Commands.Play
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

class Test_Register_Play_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Play.register_play_command(self.bot)
        self.play_command = self.bot.registered_commands.get("play")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        loop = MagicMock()
        loop.create_task = Mock()

        context = Mock(
            send    = AsyncMock(),
            guild   = Mock(),
            author  = Mock(),
            message = Mock(),
            bot     = Mock(loop = loop)
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME

        return context

    #######################################################################################################################
    #######################################################################################################################

    def _build_mock_music_manager(self, queue_size: int = 1) -> Mock:

        return Mock(
            enqueue_songs        = AsyncMock(return_value = queue_size),
            shuffle_normal_queue = AsyncMock(return_value = queue_size),
            reserve_processing   = AsyncMock(return_value = True)
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_play_command_registers_play_function(self) -> None:

        self.assertIsNotNone(
            self.play_command,
            _color_error_message_in_red(
                'The "register_play_command()" function should have registered the "play" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_play_calls_resume_when_no_args_provided(self) -> None:

        context = self._build_context()

        with patch("Commands.Play.resume_playback", new = AsyncMock()) as mock_resume:
            await self.play_command(context, args = "")

        mock_resume.assert_called_once_with(context)

    #######################################################################################################################
    #######################################################################################################################

    async def test_play_returns_early_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.Play.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            await self.play_command(context, args = "some song")

        self.assertEqual(
            context.send.call_count,
            0,
            _color_error_message_in_red(
                'No Discord message should be sent when connect_to_voice_channel() returns False.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_play_sends_error_when_no_songs_found(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Play.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Play.resolve_play_request",    new = AsyncMock(return_value = []))
        ):
            await self.play_command(context, args = "some song")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when no songs are found.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_play_does_not_shuffle_when_shuffle_is_false(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Play.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Play.resolve_play_request",    new = AsyncMock(return_value = [{"title": "Song"}])),
            patch("Commands.Play.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.Play.get_music_manager",        return_value = mock_manager),
            patch("Commands.Play.print")
        ):
            await Commands.Play.play(context, "some song", shuffle = False)

        mock_manager.shuffle_normal_queue.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_play_shuffles_queue_when_shuffle_is_true(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Play.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Play.resolve_play_request",    new = AsyncMock(return_value = [{"title": "Song"}])),
            patch("Commands.Play.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.Play.get_music_manager",        return_value = mock_manager),
            patch("Commands.Play.print")
        ):
            await Commands.Play.play(context, "some song", shuffle = True)

        mock_manager.shuffle_normal_queue.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_play_shuffle_is_called_before_reserve_processing(self) -> None:

        context    = self._build_context()
        call_order = []
        mock_manager = Mock(
            enqueue_songs        = AsyncMock(side_effect = lambda *_: call_order.append("enqueue") or 1),
            shuffle_normal_queue = AsyncMock(side_effect = lambda: call_order.append("shuffle") or 1),
            reserve_processing   = AsyncMock(side_effect = lambda: call_order.append("reserve") or True)
        )

        with (
            patch("Commands.Play.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Play.resolve_play_request",    new = AsyncMock(return_value = [{"title": "Song"}])),
            patch("Commands.Play.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.Play.get_music_manager",        return_value = mock_manager),
            patch("Commands.Play.print")
        ):
            await Commands.Play.play(context, "some song", shuffle = True)

        self.assertEqual(
            call_order,
            ["enqueue", "shuffle", "reserve"],
            _color_error_message_in_red(
                'shuffle_normal_queue() must be called after enqueue_songs() and before reserve_processing().'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_play_starts_worker_when_reserve_processing_returns_true(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Play.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Play.resolve_play_request",    new = AsyncMock(return_value = [{"title": "Song"}])),
            patch("Commands.Play.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.Play.get_music_manager",        return_value = mock_manager),
            patch("Commands.Play.print")
        ):
            await Commands.Play.play(context, "some song")

        context.bot.loop.create_task.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_play_does_not_start_worker_when_already_processing(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()
        mock_manager.reserve_processing = AsyncMock(return_value = False)

        with (
            patch("Commands.Play.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Play.resolve_play_request",    new = AsyncMock(return_value = [{"title": "Song"}])),
            patch("Commands.Play.get_music_manager",        return_value = mock_manager),
            patch("Commands.Play.print")
        ):
            await Commands.Play.play(context, "some song")

        context.bot.loop.create_task.assert_not_called()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
