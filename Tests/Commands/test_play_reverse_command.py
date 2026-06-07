###########################################################################################################################
#   Tests for the !play_reverse Discord bot command.                                                                      #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from typing import Any, Callable
from unittest.mock import AsyncMock, Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Commands.Play
import Commands.Play_Reverse
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_FAKE_SONGS = [
    { "title": "Song A", "playback_query": "https://youtube.com/a" },
    { "title": "Song B", "playback_query": "https://youtube.com/b" },
    { "title": "Song C", "playback_query": "https://youtube.com/c" },
]

###########################################################################################################################
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

class Test_Play_Reverse_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Play_Reverse.register_play_reverse_command(self.bot)
        self.play_reverse_command = self.bot.registered_commands.get("play_reverse")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        user      = Mock()
        user.name = "testuser"

        return Mock(
            author  = user,
            send    = AsyncMock(),
            message = Mock(add_reaction = AsyncMock()),
            bot     = Mock(user = Mock(), loop = Mock(create_task = Mock()))
        )

    #######################################################################################################################
    #######################################################################################################################

    def _build_music_manager(self) -> Mock:

        manager                   = Mock()
        manager.enqueue_songs     = AsyncMock(return_value = len(_FAKE_SONGS))
        manager.reserve_processing = AsyncMock(return_value = False)
        manager.shuffle_normal_queue = AsyncMock(return_value = len(_FAKE_SONGS))

        return manager

    #######################################################################################################################
    #######################################################################################################################

    async def test_registers_play_reverse_command(self) -> None:

        self.assertIsNotNone(
            self.play_reverse_command,
            _color_error_message_in_red(
                'register_play_reverse_command() should register a "play_reverse" command on the bot.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_play_reverse_calls_play_with_reverse_flag(self) -> None:

        context = self._build_context()

        with patch("Commands.Play_Reverse.play", new_callable = AsyncMock) as mock_play:
            await Commands.Play_Reverse.play_reverse(context, "some url")

        mock_play.assert_called_once_with(context, "some url", reverse = True)

    #######################################################################################################################
    #######################################################################################################################

    async def test_reverse_flag_reverses_songs_before_enqueuing(self) -> None:

        context      = self._build_context()
        music_manager = self._build_music_manager()

        with (
            patch("Commands.Play.connect_to_voice_channel", new_callable = AsyncMock, return_value = True),
            patch("Commands.Play.resolve_play_request",     new_callable = AsyncMock, return_value = list(_FAKE_SONGS)),
            patch("Commands.Play.send_reaction",            new_callable = AsyncMock),
            patch("Commands.Play.remove_reaction",          new_callable = AsyncMock),
            patch("Commands.Play.get_music_manager",        return_value = music_manager),
            patch("Commands.Play.print")
        ):
            await Commands.Play.play(context, "https://open.spotify.com/playlist/abc", reverse = True)

        enqueued = music_manager.enqueue_songs.call_args[0][0]

        self.assertEqual(
            enqueued,
            list(reversed(_FAKE_SONGS)),
            _color_error_message_in_red(
                f'play() with reverse=True should enqueue songs in reversed order. '
                f'Expected {list(reversed(_FAKE_SONGS))}, got {enqueued}.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_reverse_flag_false_preserves_original_order(self) -> None:

        context       = self._build_context()
        music_manager = self._build_music_manager()

        with (
            patch("Commands.Play.connect_to_voice_channel", new_callable = AsyncMock, return_value = True),
            patch("Commands.Play.resolve_play_request",     new_callable = AsyncMock, return_value = list(_FAKE_SONGS)),
            patch("Commands.Play.send_reaction",            new_callable = AsyncMock),
            patch("Commands.Play.remove_reaction",          new_callable = AsyncMock),
            patch("Commands.Play.get_music_manager",        return_value = music_manager),
            patch("Commands.Play.print")
        ):
            await Commands.Play.play(context, "https://open.spotify.com/playlist/abc", reverse = False)

        enqueued = music_manager.enqueue_songs.call_args[0][0]

        self.assertEqual(
            enqueued,
            list(_FAKE_SONGS),
            _color_error_message_in_red(
                f'play() with reverse=False should enqueue songs in original order. '
                f'Expected {list(_FAKE_SONGS)}, got {enqueued}.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
