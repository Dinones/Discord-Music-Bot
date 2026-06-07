###########################################################################################################################
#   Tests for the !playnext Discord bot command.                                                                         #
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

import Commands.PlayNext
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

class Test_Register_PlayNext_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.PlayNext.register_playnext_command(self.bot)
        self.playnext_command = self.bot.registered_commands.get("playnext")

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

    def _build_mock_music_manager(self) -> Mock:

        return Mock(
            enqueue_songs            = AsyncMock(return_value = 3),
            enqueue_priority_song    = AsyncMock(return_value = 1),
            push_priority_song_front = AsyncMock(return_value = 1),
            shuffle_normal_queue     = AsyncMock(return_value = 3),
            reserve_processing       = AsyncMock(return_value = True)
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_playnext_command_registers_playnext_function(self) -> None:

        self.assertIsNotNone(
            self.playnext_command,
            _color_error_message_in_red(
                'The "register_playnext_command()" function should have registered the "playnext" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_calls_resume_when_no_args_provided(self) -> None:

        context = self._build_context()

        with patch("Commands.PlayNext.resume_playback", new = AsyncMock()) as mock_resume:
            await self.playnext_command(context, args = "")

        mock_resume.assert_called_once_with(context)

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_returns_early_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            await self.playnext_command(context, args = "some song")

        self.assertEqual(
            context.send.call_count,
            0,
            _color_error_message_in_red(
                'No Discord message should be sent when connect_to_voice_channel() returns False.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_sends_error_when_no_songs_found(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = []))
        ):
            await self.playnext_command(context, args = "some song")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one error message when no songs are found.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_adds_single_song_to_priority_queue(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()
        song         = {"title": "Single Song"}

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = [song])),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.PlayNext.print")
        ):
            await self.playnext_command(context, args = "some song")

        mock_manager.enqueue_priority_song.assert_called_once_with(song)

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_does_not_touch_normal_queue_for_single_song(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = [{"title": "Song"}])),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.PlayNext.print")
        ):
            await self.playnext_command(context, args = "some song")

        mock_manager.enqueue_songs.assert_not_called()
        mock_manager.shuffle_normal_queue.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_adds_playlist_to_normal_queue_with_shuffle(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()
        songs        = [{"title": "Song A"}, {"title": "Song B"}, {"title": "Song C"}]

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = songs)),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.PlayNext.print")
        ):
            await self.playnext_command(context, args = "some playlist")

        mock_manager.enqueue_songs.assert_called_once_with(songs)
        mock_manager.shuffle_normal_queue.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_does_not_touch_priority_queue_for_playlist(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()
        songs        = [{"title": "Song A"}, {"title": "Song B"}]

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = songs)),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.PlayNext.print")
        ):
            await self.playnext_command(context, args = "some playlist")

        mock_manager.enqueue_priority_song.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_sends_playlist_warning_message_for_multiple_songs(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()
        songs        = [{"title": "Song A"}, {"title": "Song B"}]

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = songs)),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.PlayNext.print")
        ):
            await self.playnext_command(context, args = "some playlist")

        self.assertEqual(
            context.send.call_count,
            1,
            _color_error_message_in_red(
                'Should send exactly one playlist warning message when multiple songs are found.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_starts_worker_when_reserve_processing_returns_true(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = [{"title": "Song"}])),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.PlayNext.print")
        ):
            await self.playnext_command(context, args = "some song")

        context.bot.loop.create_task.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_does_not_start_worker_when_already_processing(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()
        mock_manager.reserve_processing = AsyncMock(return_value = False)

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = [{"title": "Song"}])),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.print")
        ):
            await self.playnext_command(context, args = "some song")

        context.bot.loop.create_task.assert_not_called()

    async def test_playnext_with_priority_front_pushes_song_to_front_of_priority_queue(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()
        song         = {"title": "Priority Front Song"}

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = [song])),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.PlayNext.print")
        ):
            await Commands.PlayNext.playnext(context, args = "some song", priority_front = True)

        mock_manager.push_priority_song_front.assert_called_once_with(song)
        mock_manager.enqueue_priority_song.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_returns_true_for_single_song(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = [{"title": "Song"}])),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.PlayNext.print")
        ):
            result = await Commands.PlayNext.playnext(context, args = "some song")

        self.assertTrue(
            result,
            _color_error_message_in_red(
                'playnext() should return True when a single song is successfully queued.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_playnext_returns_false_for_playlist(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()
        songs        = [{"title": "Song A"}, {"title": "Song B"}]

        with (
            patch("Commands.PlayNext.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.PlayNext.resolve_play_request",    new = AsyncMock(return_value = songs)),
            patch("Commands.PlayNext.get_music_manager",        return_value = mock_manager),
            patch("Commands.PlayNext.process_global_queue",    new = Mock(return_value = None)),
            patch("Commands.PlayNext.print")
        ):
            result = await Commands.PlayNext.playnext(context, args = "some playlist")

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'playnext() should return False when a playlist is processed.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
