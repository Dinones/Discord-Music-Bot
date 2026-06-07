###########################################################################################################################
#   Tests for the !filter Discord bot command.                                                                            #
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

import discord
import Commands.Filter
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_FAKE_GENRE_FILTERS = {"🪩 Reggaeton": ["Bad Bunny"], "🥘 Catalan": ["Els Pets"]}

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

class Test_Filter_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.music_manager = Music_Manager()

        self.bot = _Fake_Bot()

        with patch("Commands.Filter.get_music_manager", return_value = self.music_manager):
            Commands.Filter.register_filter_command(self.bot)

        self.filter_command = self.bot.registered_commands.get("filter")

    #######################################################################################################################
    #######################################################################################################################

    def _build_interaction(self) -> Mock:

        user      = Mock()
        user.name = "testuser"

        return Mock(
            response = Mock(edit_message = AsyncMock()),
            user     = user
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_registers_filter_command(self) -> None:

        self.assertIsNotNone(
            self.filter_command,
            _color_error_message_in_red(
                'register_filter_command() should register a "filter" command on the bot.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_filter_command_sends_message_with_view(self) -> None:

        context = Mock(send = AsyncMock())

        with patch("Commands.Filter.get_music_manager", return_value = self.music_manager):
            with patch("Utils.Constants.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
                await self.filter_command(context)

        context.send.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_button_starts_green_when_filter_is_inactive(self) -> None:

        with patch("Commands.Filter.get_music_manager", return_value = self.music_manager):
            button = Commands.Filter._Filter_Button("🪩 Reggaeton")

        self.assertEqual(
            button.style,
            discord.ButtonStyle.success,
            _color_error_message_in_red(
                '_Filter_Button should start with success (green) style when the genre is not in active_filters.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_button_starts_red_when_filter_is_already_active(self) -> None:

        self.music_manager.active_filters.add("🪩 Reggaeton")

        with patch("Commands.Filter.get_music_manager", return_value = self.music_manager):
            button = Commands.Filter._Filter_Button("🪩 Reggaeton")

        self.assertEqual(
            button.style,
            discord.ButtonStyle.danger,
            _color_error_message_in_red(
                '_Filter_Button should start with danger (red) style when the genre is already in active_filters.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_callback_activates_filter_and_turns_button_red(self) -> None:

        interaction = self._build_interaction()

        with patch("Commands.Filter.get_music_manager", return_value = self.music_manager):
            button = Commands.Filter._Filter_Button("🪩 Reggaeton")
            with patch("Commands.Filter.print"):
                await button.callback(interaction)

        self.assertIn(
            "🪩 Reggaeton",
            self.music_manager.active_filters,
            _color_error_message_in_red(
                'callback() should add the genre to active_filters when it was inactive.'
            )
        )
        self.assertEqual(
            button.style,
            discord.ButtonStyle.danger,
            _color_error_message_in_red(
                'callback() should switch button style to danger (red) when activating a filter.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_callback_deactivates_filter_and_turns_button_green(self) -> None:

        self.music_manager.active_filters.add("🪩 Reggaeton")
        interaction = self._build_interaction()

        with patch("Commands.Filter.get_music_manager", return_value = self.music_manager):
            button = Commands.Filter._Filter_Button("🪩 Reggaeton")
            with patch("Commands.Filter.print"):
                await button.callback(interaction)

        self.assertNotIn(
            "🪩 Reggaeton",
            self.music_manager.active_filters,
            _color_error_message_in_red(
                'callback() should remove the genre from active_filters when it was active.'
            )
        )
        self.assertEqual(
            button.style,
            discord.ButtonStyle.success,
            _color_error_message_in_red(
                'callback() should switch button style to success (green) when deactivating a filter.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_callback_calls_edit_message_on_interaction(self) -> None:

        interaction = self._build_interaction()

        with patch("Commands.Filter.get_music_manager", return_value = self.music_manager):
            button = Commands.Filter._Filter_Button("🪩 Reggaeton")
            with patch("Commands.Filter.print"):
                await button.callback(interaction)

        interaction.response.edit_message.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_filter_view_creates_one_button_per_genre(self) -> None:

        with patch("Commands.Filter.get_music_manager", return_value = self.music_manager):
            with patch("Utils.Constants.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
                view = Commands.Filter._Filter_View()

        self.assertEqual(
            len(view.children),
            len(_FAKE_GENRE_FILTERS),
            _color_error_message_in_red(
                '_Filter_View should create exactly one button per genre in GENRE_FILTERS.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
