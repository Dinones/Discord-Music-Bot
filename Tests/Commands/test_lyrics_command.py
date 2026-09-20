###########################################################################################################################
#   Tests for the !lyrics Discord bot command and the _format_timestamp() helper.                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from typing import Any, Callable, List, Tuple
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Commands.Lyrics
import Utils.Constants as CONST
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_FAKE_SONG: dict = {
    "title"         : "Test Song",
    "playback_query": "https://www.youtube.com/watch?v=test123",
}

# Nine lines, 15 s apart. At elapsed=60 s (sync_offset=0) → current_idx=4 ("chorus"), window shows indices 1-7.
_FAKE_LYRICS: List[Tuple[float, str]] = [
    (0.0,   "intro"),
    (15.0,  "verse 1"),
    (30.0,  "verse 2"),
    (45.0,  "verse 3"),
    (60.0,  "chorus"),
    (75.0,  "verse 4"),
    (90.0,  "verse 5"),
    (105.0, "verse 6"),
    (120.0, "outro"),
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

class Test_Format_Timestamp(unittest.TestCase):

    def test_formats_zero_seconds(self) -> None:

        self.assertEqual(
            Commands.Lyrics._format_timestamp(0.0),
            "[0:00]",
            _color_error_message_in_red("_format_timestamp(0.0) should return '[0:00]'.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_formats_whole_minutes(self) -> None:

        self.assertEqual(
            Commands.Lyrics._format_timestamp(90.0),
            "[1:30]",
            _color_error_message_in_red("_format_timestamp(90.0) should return '[1:30]'.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_pads_single_digit_seconds(self) -> None:

        self.assertEqual(
            Commands.Lyrics._format_timestamp(65.0),
            "[1:05]",
            _color_error_message_in_red("_format_timestamp(65.0) should zero-pad seconds to two digits: '[1:05]'.")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_truncates_fractional_seconds(self) -> None:

        self.assertEqual(
            Commands.Lyrics._format_timestamp(65.9),
            "[1:05]",
            _color_error_message_in_red("_format_timestamp(65.9) should truncate (not round) to '[1:05]'.")
        )

###########################################################################################################################
###########################################################################################################################

class Test_Lyrics_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.Lyrics.register_lyrics_command(self.bot)
        self.lyrics_command = self.bot.registered_commands.get("lyrics")

    #######################################################################################################################
    #######################################################################################################################

    def _build_context(self) -> Mock:

        context             = Mock(send = AsyncMock())
        context.author      = Mock()
        context.author.name = CONST.TESTING_AUTHOR_NAME

        return context

    #######################################################################################################################
    #######################################################################################################################

    def _build_updater(self) -> Mock:

        updater                  = Mock()
        updater._lyrics_ready    = True
        updater._lyrics          = list(_FAKE_LYRICS)
        updater._sync_offset     = 0.0
        updater._play_start_time = 0.0
        updater._paused_acc      = 0.0
        updater._seek_offset     = 0

        return updater

    #######################################################################################################################
    #######################################################################################################################

    def _build_music_manager(self) -> Mock:

        mm               = Mock()
        mm.current_song    = dict(_FAKE_SONG)
        mm.current_updater = self._build_updater()

        return mm

    #######################################################################################################################
    #######################################################################################################################

    async def test_registers_lyrics_command(self) -> None:

        self.assertIsNotNone(
            self.lyrics_command,
            _color_error_message_in_red('register_lyrics_command() should register a "lyrics" command on the bot.')
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_error_when_not_playing(self) -> None:

        context         = self._build_context()
        mm              = self._build_music_manager()
        mm.current_song = None

        with patch("Commands.Lyrics.get_music_manager", return_value = mm):
            await self.lyrics_command(context)

        context.send.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_error_when_updater_is_none(self) -> None:

        context            = self._build_context()
        mm                 = self._build_music_manager()
        mm.current_updater = None

        with patch("Commands.Lyrics.get_music_manager", return_value = mm):
            await self.lyrics_command(context)

        context.send.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_error_when_lyrics_not_ready(self) -> None:

        context                           = self._build_context()
        mm                                = self._build_music_manager()
        mm.current_updater._lyrics_ready  = False

        with patch("Commands.Lyrics.get_music_manager", return_value = mm):
            await self.lyrics_command(context)

        context.send.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_error_when_lyrics_unavailable(self) -> None:

        context                      = self._build_context()
        mm                           = self._build_music_manager()
        mm.current_updater._lyrics   = None

        with patch("Commands.Lyrics.get_music_manager", return_value = mm):
            await self.lyrics_command(context)

        context.send.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_embed_on_success(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        context.send.assert_called_once()
        _, kwargs = context.send.call_args

        self.assertIn(
            "embed",
            kwargs,
            _color_error_message_in_red("lyrics() should send a discord.Embed via the 'embed' keyword argument.")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_embed_title_matches_song_title(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs = context.send.call_args

        self.assertEqual(
            kwargs["embed"].title,
            "Test Song",
            _color_error_message_in_red("Embed title should match the current song's title.")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_embed_url_uses_playback_query(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs = context.send.call_args

        self.assertEqual(
            kwargs["embed"].url,
            "https://www.youtube.com/watch?v=test123",
            _color_error_message_in_red("Embed URL should be the song's playback_query (YouTube URL).")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_embed_url_falls_back_to_spotify_url(self) -> None:

        context          = self._build_context()
        mm               = self._build_music_manager()
        mm.current_song  = {"title": "Spotify Song", "spotify_url": "https://open.spotify.com/track/abc"}

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs = context.send.call_args

        self.assertEqual(
            kwargs["embed"].url,
            "https://open.spotify.com/track/abc",
            _color_error_message_in_red("Embed URL should fall back to spotify_url when playback_query is absent.")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_embed_url_is_empty_when_no_url_fields(self) -> None:

        context          = self._build_context()
        mm               = self._build_music_manager()
        mm.current_song  = {"title": "No URL Song"}

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs = context.send.call_args

        self.assertEqual(
            kwargs["embed"].url,
            "",
            _color_error_message_in_red(
                "Embed URL should be an empty string when neither playback_query nor spotify_url is present."
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_current_line_is_marked_with_arrow(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()
        # loop.time()=60, play_start=0, paused_acc=0, seek_offset=0, sync_offset=0 → adjusted=60 → idx 4 ("chorus")

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs     = context.send.call_args
        description   = kwargs["embed"].description
        current_lines = [line for line in description.splitlines() if "▶" in line]

        self.assertEqual(
            len(current_lines),
            1,
            _color_error_message_in_red("Exactly one line in the embed description should be marked with ▶.")
        )
        self.assertIn(
            "chorus",
            current_lines[0],
            _color_error_message_in_red("The line marked with ▶ should contain the active lyric text ('chorus').")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_non_current_lines_do_not_have_arrow(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs     = context.send.call_args
        description   = kwargs["embed"].description
        non_current   = [line for line in description.splitlines() if "▶" not in line]

        self.assertGreater(
            len(non_current),
            0,
            _color_error_message_in_red("There should be surrounding lines in the description without ▶.")
        )
        for line in non_current:
            self.assertNotIn(
                "▶",
                line,
                _color_error_message_in_red(f"Non-current line should not contain ▶: {line!r}")
            )

    #######################################################################################################################
    #######################################################################################################################

    async def test_first_line_is_active_before_any_timestamp(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()
        # First lyric starts at 10 s; with elapsed=2 s the loop breaks immediately (ts[0]=10 > 2)
        # so current_idx stays at 0 and the first line is shown as active.
        mm.current_updater._lyrics = [
            (10.0,  "first line"),
            (30.0,  "second line"),
            (50.0,  "third line"),
        ]

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 2.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs   = context.send.call_args
        description = kwargs["embed"].description
        active_line = next(line for line in description.splitlines() if "▶" in line)

        self.assertIn(
            "first line",
            active_line,
            _color_error_message_in_red(
                "When elapsed is before the first lyric timestamp, the first line should be shown as active."
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_last_line_is_active_past_all_timestamps(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()
        # loop.time()=200 → elapsed=200 > 120 (last ts) → current_idx=8 ("outro")

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 200.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs   = context.send.call_args
        description = kwargs["embed"].description
        active_line = next(line for line in description.splitlines() if "▶" in line)

        self.assertIn(
            "outro",
            active_line,
            _color_error_message_in_red(
                "When elapsed is past all lyric timestamps, the last line should be shown as active."
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sync_offset_shifts_active_line_selection(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()
        # elapsed=75, sync_offset=15 → adjusted=60 → "chorus" (idx 4)
        # Without the offset: adjusted=75 → "verse 4" (idx 5) would be active instead
        mm.current_updater._sync_offset = 15.0

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 75.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs   = context.send.call_args
        description = kwargs["embed"].description
        active_line = next(line for line in description.splitlines() if "▶" in line)

        self.assertIn(
            "chorus",
            active_line,
            _color_error_message_in_red(
                "sync_offset must be subtracted from elapsed before searching the lyrics list. "
                "With elapsed=75 s and sync_offset=15 s, adjusted=60 s → 'chorus' should be active, not 'verse 4'."
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_paused_time_is_excluded_from_elapsed(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()
        # loop.time()=80, paused_acc=20 → elapsed=60 → "chorus" (idx 4)
        # Without subtracting paused_acc: elapsed=80 → "verse 4" (idx 5) would be active instead
        mm.current_updater._paused_acc = 20.0

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 80.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs   = context.send.call_args
        description = kwargs["embed"].description
        active_line = next(line for line in description.splitlines() if "▶" in line)

        self.assertIn(
            "chorus",
            active_line,
            _color_error_message_in_red(
                "_paused_acc must be subtracted from elapsed. "
                "With loop.time()=80 s and paused_acc=20 s, elapsed=60 s → 'chorus' should be active, not 'verse 4'."
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_shows_correct_number_of_lines_in_window(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()
        # current_idx=4 has 3 lines before and 4 after in _FAKE_LYRICS → full window of 7 lines

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs   = context.send.call_args
        line_count  = len(kwargs["embed"].description.splitlines())
        expected    = 2 * Commands.Lyrics._WINDOW_SIZE + 1

        self.assertEqual(
            line_count,
            expected,
            _color_error_message_in_red(
                f"With enough surrounding lyrics the embed should show {expected} lines "
                f"({Commands.Lyrics._WINDOW_SIZE} before + 1 current + {Commands.Lyrics._WINDOW_SIZE} after)."
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_window_clamped_at_start(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()
        # elapsed=15 → current_idx=1, start=max(0,1-3)=0, end=min(9,1+4)=5 → 5 lines, not the full 7

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 15.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs  = context.send.call_args
        line_count = len(kwargs["embed"].description.splitlines())

        self.assertLess(
            line_count,
            2 * Commands.Lyrics._WINDOW_SIZE + 1,
            _color_error_message_in_red(
                "When the active line is near the start of the lyrics list the window should be "
                "clamped to the available lines rather than trying to show WINDOW_SIZE previous lines."
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_window_clamped_at_end(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()
        # elapsed=120 → current_idx=8 (last), start=max(0,8-3)=5, end=min(9,8+4)=9 → 4 lines, not 7

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 120.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs  = context.send.call_args
        line_count = len(kwargs["embed"].description.splitlines())

        self.assertLess(
            line_count,
            2 * Commands.Lyrics._WINDOW_SIZE + 1,
            _color_error_message_in_red(
                "When the active line is near the end of the lyrics list the window should be "
                "clamped to the available lines rather than extending past the end."
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_empty_text_shows_music_label(self) -> None:

        context = self._build_context()
        mm      = self._build_music_manager()
        # "chorus" replaced with an empty string to simulate an instrumental section
        mm.current_updater._lyrics = [
            (0.0,   "intro"),
            (15.0,  "verse 1"),
            (30.0,  "verse 2"),
            (45.0,  "verse 3"),
            (60.0,  ""),
            (75.0,  "verse 4"),
            (90.0,  "verse 5"),
            (105.0, "verse 6"),
            (120.0, "outro"),
        ]

        with (
            patch("Commands.Lyrics.get_music_manager", return_value = mm),
            patch("Commands.Lyrics.asyncio.get_running_loop", return_value = Mock(time = Mock(return_value = 60.0))),
            patch("Commands.Lyrics.print")
        ):
            await self.lyrics_command(context)

        _, kwargs   = context.send.call_args
        description = kwargs["embed"].description
        active_line = next(line for line in description.splitlines() if "▶" in line)

        self.assertIn(
            "(Music)",
            active_line,
            _color_error_message_in_red(
                "An empty lyric line should display '(Music)' instead of blank text in the embed."
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
