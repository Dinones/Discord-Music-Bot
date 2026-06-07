###########################################################################################################################
#   Tests for the !shuffle and !mix Discord bot commands.                                                                #
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

import Commands.Shuffle
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

class Test_Register_Shuffle_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Shuffle.register_shuffle_command(self.bot)
        self.shuffle_command = self.bot.registered_commands.get("shuffle")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        context = Mock(
            send    = AsyncMock(),
            guild   = Mock(),
            author  = Mock(),
            message = Mock()
        )

        context.author.name = CONST.TESTING_AUTHOR_NAME

        return context

    #######################################################################################################################
    #######################################################################################################################

    def _build_mock_music_manager(self, shuffled_count: int = 3) -> Mock:

        return Mock(shuffle_normal_queue = AsyncMock(return_value = shuffled_count))

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_shuffle_command_registers_shuffle_function(self) -> None:

        self.assertIsNotNone(
            self.shuffle_command,
            _color_error_message_in_red(
                'The "register_shuffle_command()" function should have registered the "shuffle" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_shuffle_returns_zero_when_connect_to_voice_channel_fails(self) -> None:

        context = self._build_context()

        with patch("Commands.Shuffle.connect_to_voice_channel", new = AsyncMock(return_value = False)):
            result = await Commands.Shuffle.shuffle(context)

        self.assertEqual(
            result,
            0,
            _color_error_message_in_red(
                'shuffle() should return 0 when connect_to_voice_channel() returns False.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_shuffle_sends_reaction_when_successful(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Shuffle.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Shuffle.get_music_manager", return_value = mock_manager),
            patch("Commands.Shuffle.send_reaction", new = AsyncMock(return_value = True)) as mock_reaction,
            patch("Commands.Shuffle.print")
        ):
            await Commands.Shuffle.shuffle(context)

        mock_reaction.assert_called_once_with(context.message, "✅")

    #######################################################################################################################
    #######################################################################################################################

    async def test_shuffle_does_not_send_reaction_when_feedback_disabled(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager()

        with (
            patch("Commands.Shuffle.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Shuffle.get_music_manager", return_value = mock_manager),
            patch("Commands.Shuffle.send_reaction", new = AsyncMock()) as mock_reaction
        ):
            await Commands.Shuffle.shuffle(context, send_feedback = False)

        mock_reaction.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_shuffle_returns_shuffled_song_count(self) -> None:

        context      = self._build_context()
        mock_manager = self._build_mock_music_manager(shuffled_count = 7)

        with (
            patch("Commands.Shuffle.connect_to_voice_channel", new = AsyncMock(return_value = True)),
            patch("Commands.Shuffle.get_music_manager", return_value = mock_manager),
            patch("Commands.Shuffle.send_reaction", new = AsyncMock()),
            patch("Commands.Shuffle.print")
        ):
            result = await Commands.Shuffle.shuffle(context)

        self.assertEqual(
            result,
            7,
            _color_error_message_in_red(
                'shuffle() should return the number of songs shuffled by the music manager.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
