###########################################################################################################################
#   Tests for the !download Discord bot command.                                                                          #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from typing import Any, Callable
from unittest.mock import MagicMock, Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Commands.Download
import Utils.Constants as CONST
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_MB = 1024 * 1024

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

def _fake_tmpdir(path: str = "/fake/tmp") -> MagicMock:

    cm                        = MagicMock()
    cm.__enter__.return_value = path
    cm.__exit__.return_value  = False

    return cm

###########################################################################################################################
###########################################################################################################################

class Test_Register_Download_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Download.register_download_command(self.bot)
        self.download_command = self.bot.registered_commands.get("download")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self, filesize_limit: int = 25 * _MB) -> Mock:

        context                      = Mock()
        context.send                 = AsyncMock()
        context.author               = Mock()
        context.author.name          = CONST.TESTING_AUTHOR_NAME
        context.message              = Mock()
        context.bot                  = Mock()
        context.bot.user             = Mock()
        context.guild                = Mock()
        context.guild.filesize_limit = filesize_limit

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_download_command_registers_download_function(self) -> None:

        self.assertIsNotNone(
            self.download_command,
            _color_error_message_in_red(
                'register_download_command() should have registered the "download" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_error_reaction_when_args_is_empty(self) -> None:

        context = self._build_context()

        with patch("Commands.Download.send_reaction", new = AsyncMock()) as mock_reaction:
            await self.download_command(context)

        mock_reaction.assert_called_once_with(context.message, "❌")

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_message_when_args_is_empty(self) -> None:

        context = self._build_context()

        with patch("Commands.Download.send_reaction", new = AsyncMock()):
            await self.download_command(context)

        context.send.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_error_reaction_when_spotify_url_provided(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Download.is_spotify_url",  return_value = True),
            patch("Commands.Download.send_reaction",   new = AsyncMock()) as mock_reaction,
        ):
            await self.download_command(context, args = "https://open.spotify.com/track/abc")

        mock_reaction.assert_called_once_with(context.message, "❌")

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_loading_reaction_before_download_starts(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Download.is_spotify_url",  return_value = False),
            patch("Commands.Download.send_reaction",   new = AsyncMock()) as mock_reaction,
            patch("Commands.Download.remove_reaction", new = AsyncMock()),
            patch("Commands.Download.get_music_manager", return_value = Mock()),
            patch("Commands.Download.download_mp3",    new = AsyncMock(return_value = None)),
            patch("Commands.Download.tempfile.TemporaryDirectory", return_value = _fake_tmpdir()),
            patch("Commands.Download.print"),
        ):
            await self.download_command(context, args = "some query")

        sent_reactions = [call.args[1] for call in mock_reaction.call_args_list]

        self.assertIn(
            "⏳",
            sent_reactions,
            _color_error_message_in_red(
                'download() should add a "⏳" loading reaction before starting the download.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_error_when_download_mp3_fails(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Download.is_spotify_url",  return_value = False),
            patch("Commands.Download.send_reaction",   new = AsyncMock()),
            patch("Commands.Download.remove_reaction", new = AsyncMock()),
            patch("Commands.Download.get_music_manager", return_value = Mock()),
            patch("Commands.Download.download_mp3",    new = AsyncMock(return_value = None)),
            patch("Commands.Download.tempfile.TemporaryDirectory", return_value = _fake_tmpdir()),
            patch("Commands.Download.print"),
        ):
            await self.download_command(context, args = "some query")

        context.send.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_error_when_no_mp3_found_in_tmpdir(self) -> None:

        context = self._build_context()

        with (
            patch("Commands.Download.is_spotify_url",  return_value = False),
            patch("Commands.Download.send_reaction",   new = AsyncMock()),
            patch("Commands.Download.remove_reaction", new = AsyncMock()),
            patch("Commands.Download.get_music_manager", return_value = Mock()),
            patch("Commands.Download.download_mp3",    new = AsyncMock(return_value = "file:///fake/tmp/song.mp3")),
            patch("Commands.Download.os.listdir",      return_value = ["cover.png", "info.json"]),
            patch("Commands.Download.tempfile.TemporaryDirectory", return_value = _fake_tmpdir()),
            patch("Commands.Download.print"),
        ):
            await self.download_command(context, args = "some query")

        context.send.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_error_when_file_exceeds_guild_limit(self) -> None:

        context = self._build_context(filesize_limit = 8 * _MB)

        with (
            patch("Commands.Download.is_spotify_url",    return_value = False),
            patch("Commands.Download.send_reaction",     new = AsyncMock()),
            patch("Commands.Download.remove_reaction",   new = AsyncMock()),
            patch("Commands.Download.get_music_manager", return_value = Mock()),
            patch("Commands.Download.download_mp3",      new = AsyncMock(return_value = "file:///fake/tmp/song.mp3")),
            patch("Commands.Download.os.listdir",        return_value = ["song.mp3"]),
            patch("Commands.Download.os.path.getsize",   return_value = 50 * _MB),
            patch("Commands.Download.tempfile.TemporaryDirectory", return_value = _fake_tmpdir()),
            patch("Commands.Download.print"),
        ):
            await self.download_command(context, args = "some query")

        context.send.assert_called_once()
        sent_text = context.send.call_args[0][0]

        self.assertIn(
            "MB",
            sent_text,
            _color_error_message_in_red(
                'download() should include MB values in the file-too-large error message.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_file_as_discord_attachment_on_success(self) -> None:

        context    = self._build_context(filesize_limit = 25 * _MB)
        mock_file  = Mock()

        with (
            patch("Commands.Download.is_spotify_url",    return_value = False),
            patch("Commands.Download.send_reaction",     new = AsyncMock()),
            patch("Commands.Download.remove_reaction",   new = AsyncMock()),
            patch("Commands.Download.get_music_manager", return_value = Mock()),
            patch("Commands.Download.download_mp3",      new = AsyncMock(return_value = "file:///fake/tmp/song.mp3")),
            patch("Commands.Download.os.listdir",        return_value = ["song.mp3"]),
            patch("Commands.Download.os.path.getsize",   return_value = 5 * _MB),
            patch("Commands.Download.discord.File",      return_value = mock_file),
            patch("Commands.Download.tempfile.TemporaryDirectory", return_value = _fake_tmpdir("/fake/tmp")),
            patch("Commands.Download.print"),
        ):
            await self.download_command(context, args = "some query")

        context.send.assert_called_once()
        _, kwargs = context.send.call_args

        self.assertEqual(
            kwargs.get("file"),
            mock_file,
            _color_error_message_in_red(
                'download() should send the downloaded MP3 as a discord.File attachment.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_adds_success_reaction_and_removes_loading_on_success(self) -> None:

        context = self._build_context(filesize_limit = 25 * _MB)

        with (
            patch("Commands.Download.is_spotify_url",    return_value = False),
            patch("Commands.Download.send_reaction",     new = AsyncMock()) as mock_reaction,
            patch("Commands.Download.remove_reaction",   new = AsyncMock()) as mock_remove,
            patch("Commands.Download.get_music_manager", return_value = Mock()),
            patch("Commands.Download.download_mp3",      new = AsyncMock(return_value = "file:///fake/tmp/song.mp3")),
            patch("Commands.Download.os.listdir",        return_value = ["song.mp3"]),
            patch("Commands.Download.os.path.getsize",   return_value = 5 * _MB),
            patch("Commands.Download.discord.File",      return_value = Mock()),
            patch("Commands.Download.tempfile.TemporaryDirectory", return_value = _fake_tmpdir("/fake/tmp")),
            patch("Commands.Download.print"),
        ):
            await self.download_command(context, args = "some query")

        sent_reactions = [call.args[1] for call in mock_reaction.call_args_list]
        removed_reactions = [call.args[1] for call in mock_remove.call_args_list]

        self.assertIn(
            "✅",
            sent_reactions,
            _color_error_message_in_red(
                'download() should add a "✅" reaction on successful file upload.'
            )
        )

        self.assertIn(
            "⏳",
            removed_reactions,
            _color_error_message_in_red(
                'download() should remove the "⏳" loading reaction after completing.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
