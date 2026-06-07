###########################################################################################################################
#   Tests for the !playlists Discord bot command.                                                                        #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from typing import Any, Callable
from unittest.mock import ANY, AsyncMock, Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import discord
import Commands.Playlists
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_FAKE_PLAYLISTS = [
    { "name": "Chill",   "url": "https://open.spotify.com/playlist/abc" },
    { "name": "Workout", "url": "https://open.spotify.com/playlist/xyz" },
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

class Test_Playlists_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Playlists.register_playlists_command(self.bot)
        self.playlists_command = self.bot.registered_commands.get("playlists")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        author      = Mock()
        author.name = "testuser"

        return Mock(
            author = author,
            send   = AsyncMock(),
            bot    = Mock()
        )

    #######################################################################################################################
    #######################################################################################################################

    def _build_interaction(self) -> Mock:

        user      = Mock()
        user.name = "testuser"

        interaction          = Mock()
        interaction.response = Mock(defer = AsyncMock())
        interaction.message  = Mock(delete = AsyncMock())
        interaction.user     = user
        interaction.guild    = Mock()
        interaction.channel  = Mock(send = AsyncMock())

        return interaction

    #######################################################################################################################
    #######################################################################################################################

    async def test_registers_playlists_command(self) -> None:

        self.assertIsNotNone(
            self.playlists_command,
            _color_error_message_in_red(
                'register_playlists_command() should register a "playlists" command on the bot.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_panel_with_view_when_playlists_configured(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Playlists.get_playlists", return_value = _FAKE_PLAYLISTS),
            patch("Commands.Playlists.print")
        ):
            await self.playlists_command(context)

        context.send.assert_called_once()
        _, kwargs = context.send.call_args
        self.assertIsInstance(
            kwargs.get("view"),
            discord.ui.View,
            _color_error_message_in_red(
                'playlists() should send a message with a discord.ui.View when playlists are configured.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_no_playlists_message_when_list_is_empty(self) -> None:

        context = self._build_context()

        with patch("Commands.Playlists.get_playlists", return_value = []):
            await self.playlists_command(context)

        context.send.assert_called_once()
        self.assertNotIn(
            "view",
            context.send.call_args.kwargs,
            _color_error_message_in_red(
                'playlists() should not send a view when the playlist list is empty.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_view_creates_one_button_per_playlist(self) -> None:

        with patch("Commands.Playlists.get_playlists", return_value = _FAKE_PLAYLISTS):
            view = Commands.Playlists._Playlists_View(Mock())

        self.assertEqual(
            len(view.children),
            len(_FAKE_PLAYLISTS),
            _color_error_message_in_red(
                f'_Playlists_View should create exactly {len(_FAKE_PLAYLISTS)} buttons, '
                f'one per playlist, instead of {len(view.children)}.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_button_label_matches_playlist_name(self) -> None:

        with patch("Commands.Playlists.get_playlists", return_value = _FAKE_PLAYLISTS):
            view = Commands.Playlists._Playlists_View(Mock())

        labels   = [btn.label for btn in view.children]
        expected = [p["name"] for p in _FAKE_PLAYLISTS]

        self.assertEqual(
            labels,
            expected,
            _color_error_message_in_red(
                f'Button labels should match playlist names {expected} instead of {labels}.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_button_callback_defers_interaction(self) -> None:

        with patch("Commands.Playlists.get_playlists", return_value = _FAKE_PLAYLISTS):
            view   = Commands.Playlists._Playlists_View(Mock())
            button = view.children[0]

        interaction = self._build_interaction()

        with (
            patch("Commands.Playlists.clear", new_callable = AsyncMock),
            patch("Commands.Playlists.play",  new_callable = AsyncMock),
            patch("Commands.Playlists.print")
        ):
            await button.callback(interaction)

        interaction.response.defer.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_button_callback_deletes_message(self) -> None:

        with patch("Commands.Playlists.get_playlists", return_value = _FAKE_PLAYLISTS):
            view   = Commands.Playlists._Playlists_View(Mock())
            button = view.children[0]

        interaction = self._build_interaction()

        with (
            patch("Commands.Playlists.clear", new_callable = AsyncMock),
            patch("Commands.Playlists.play",  new_callable = AsyncMock),
            patch("Commands.Playlists.print")
        ):
            await button.callback(interaction)

        interaction.message.delete.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_button_callback_calls_clear_without_feedback(self) -> None:

        with patch("Commands.Playlists.get_playlists", return_value = _FAKE_PLAYLISTS):
            view   = Commands.Playlists._Playlists_View(Mock())
            button = view.children[0]

        interaction = self._build_interaction()

        with (
            patch("Commands.Playlists.clear", new_callable = AsyncMock) as mock_clear,
            patch("Commands.Playlists.play",  new_callable = AsyncMock),
            patch("Commands.Playlists.print")
        ):
            await button.callback(interaction)

        mock_clear.assert_called_once_with(ANY, send_feedback = False)
        ctx_arg = mock_clear.call_args[0][0]
        self.assertIsInstance(
            ctx_arg,
            Commands.Playlists._Interaction_Context,
            _color_error_message_in_red(
                'Button callback should call clear() with an _Interaction_Context built from the interaction.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_button_callback_calls_playmix_with_correct_url(self) -> None:

        with patch("Commands.Playlists.get_playlists", return_value = _FAKE_PLAYLISTS):
            view   = Commands.Playlists._Playlists_View(Mock())
            button = view.children[0]

        interaction = self._build_interaction()

        with (
            patch("Commands.Playlists.clear", new_callable = AsyncMock),
            patch("Commands.Playlists.play",  new_callable = AsyncMock) as mock_play,
            patch("Commands.Playlists.print")
        ):
            await button.callback(interaction)

        mock_play.assert_called_once_with(ANY, _FAKE_PLAYLISTS[0]["url"], shuffle = True)
        ctx_arg = mock_play.call_args[0][0]
        self.assertIsInstance(
            ctx_arg,
            Commands.Playlists._Interaction_Context,
            _color_error_message_in_red(
                'Button callback should call play() with an _Interaction_Context built from the interaction.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_button_uses_startup_message_when_provided(self) -> None:

        startup_message = Mock(add_reaction = AsyncMock(), remove_reaction = AsyncMock())
        startup_message.author      = Mock()
        startup_message.author.name = "Bot"

        with patch("Commands.Playlists.get_playlists", return_value = _FAKE_PLAYLISTS):
            view   = Commands.Playlists._Playlists_View(Mock(), startup_message)
            button = view.children[0]

        interaction = self._build_interaction()

        with (
            patch("Commands.Playlists.clear", new_callable = AsyncMock) as mock_clear,
            patch("Commands.Playlists.play",  new_callable = AsyncMock),
            patch("Commands.Playlists.print")
        ):
            await button.callback(interaction)

        ctx_arg = mock_clear.call_args[0][0]
        self.assertIs(
            ctx_arg.message,
            startup_message,
            _color_error_message_in_red(
                'When startup_message is provided, ctx.message should be that startup message, not _No_Op_Message.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_send_playlists_panel_does_nothing_when_no_playlists(self) -> None:

        channel = Mock(send = AsyncMock())
        bot     = Mock()

        with patch("Commands.Playlists.get_playlists", return_value = []):
            await Commands.Playlists.send_playlists_panel(channel, bot)

        channel.send.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_send_playlists_panel_sends_view_when_playlists_configured(self) -> None:

        channel = Mock(send = AsyncMock())
        bot     = Mock()

        with (
            patch("Commands.Playlists.get_playlists", return_value = _FAKE_PLAYLISTS),
            patch("Commands.Playlists.print")
        ):
            await Commands.Playlists.send_playlists_panel(channel, bot)

        channel.send.assert_called_once()
        _, kwargs = channel.send.call_args
        self.assertIsInstance(
            kwargs.get("view"),
            discord.ui.View,
            _color_error_message_in_red(
                'send_playlists_panel() should send a discord.ui.View to the channel.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
