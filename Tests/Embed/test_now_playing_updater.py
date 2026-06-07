###########################################################################################################################
#   Tests for Now_Playing_Updater and build_progress_bar() in Now_Playing_Updater.                                       #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
import unittest
from unittest.mock import Mock, AsyncMock, patch
from typing import Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Tests.Helpers.helpers import _color_error_message_in_red
from Utils.Embed.Now_Playing_Updater import build_progress_bar, Now_Playing_Updater

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Build_Progress_Bar(unittest.TestCase):

    #######################################################################################################################
    #######################################################################################################################

    def test_icon_is_play_when_not_paused(self) -> None:

        result = build_progress_bar(30.0, 300.0, is_paused = False)

        self.assertTrue(
            result.startswith("▶"),
            _color_error_message_in_red(
                'build_progress_bar() should start with ▶ when not paused.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_icon_is_pause_when_paused(self) -> None:

        result = build_progress_bar(30.0, 300.0, is_paused = True)

        self.assertTrue(
            result.startswith("❚❚"),
            _color_error_message_in_red(
                'build_progress_bar() should start with ❚❚ when paused.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_bar_width_is_correct(self) -> None:

        result   = build_progress_bar(50.0, 200.0, width = 20)
        bar_part = result.split("⠀")[1]

        self.assertEqual(
            len(bar_part),
            20,
            _color_error_message_in_red(
                'build_progress_bar() should produce a bar of exactly the specified width.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_elapsed_zero_shows_empty_bar(self) -> None:

        result = build_progress_bar(0.0, 300.0, width = 20)

        self.assertIn(
            "░" * 20,
            result,
            _color_error_message_in_red(
                'build_progress_bar() should show a fully empty bar when elapsed is 0.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_elapsed_equals_duration_shows_full_bar(self) -> None:

        result = build_progress_bar(300.0, 300.0, width = 20)

        self.assertIn(
            "█" * 20,
            result,
            _color_error_message_in_red(
                'build_progress_bar() should show a fully filled bar when elapsed equals duration.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_elapsed_exceeding_duration_is_clamped(self) -> None:

        result = build_progress_bar(400.0, 300.0, width = 20)

        self.assertIn(
            "█" * 20,
            result,
            _color_error_message_in_red(
                'build_progress_bar() should clamp elapsed to duration when elapsed exceeds it.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_time_format_minutes_and_seconds(self) -> None:

        result = build_progress_bar(225.0, 300.0)

        self.assertIn(
            "3:45",
            result,
            _color_error_message_in_red(
                'build_progress_bar() should format 225 seconds as "3:45".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_time_format_hours_minutes_seconds(self) -> None:

        result = build_progress_bar(3723.0, 7200.0)

        self.assertIn(
            "1:02:03",
            result,
            _color_error_message_in_red(
                'build_progress_bar() should format 3723 seconds as "1:02:03".'
            )
        )

###########################################################################################################################
###########################################################################################################################

class Test_Now_Playing_Updater(unittest.IsolatedAsyncioTestCase):

    #######################################################################################################################
    #######################################################################################################################

    def _build_updater(self, duration: float = 300.0, is_paused: bool = False) -> Tuple[Now_Playing_Updater, Mock, Mock]:

        message      = Mock(edit = AsyncMock())
        voice_client = Mock(is_paused = Mock(return_value = is_paused))
        song         = {"title": "Test Song", "duration": duration}
        updater      = Now_Playing_Updater(message, song, voice_client, start_time = 0.0)

        return updater, message, voice_client

    #######################################################################################################################
    #######################################################################################################################

    async def test_stop_before_start_is_a_noop(self) -> None:

        updater, _, _ = self._build_updater()

        try:
            await updater.stop()
        except Exception as error:
            self.fail(
                _color_error_message_in_red(
                    f'stop() before start() should not raise an exception, but raised: {error}'
                )
            )

    #######################################################################################################################
    #######################################################################################################################

    async def test_start_creates_a_task(self) -> None:

        updater, _, _ = self._build_updater()

        with patch("Utils.Embed.Now_Playing_Updater.asyncio.sleep", new = AsyncMock(side_effect = asyncio.CancelledError)):
            await updater.start()

        self.assertIsNotNone(
            updater._task,
            _color_error_message_in_red(
                'start() should assign a background task to _task.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_stop_cancels_running_task(self) -> None:

        updater, _, _ = self._build_updater()

        async def _hang() -> None:
            await asyncio.sleep(9999)

        updater._task = asyncio.create_task(_hang())
        await updater.stop()

        self.assertTrue(
            updater._task.cancelled(),
            _color_error_message_in_red(
                'stop() should cancel the running background task.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_update_loop_exits_early_when_no_duration(self) -> None:

        updater, message, _ = self._build_updater(duration = 0.0)

        await updater._update_loop()

        self.assertEqual(
            message.edit.call_count,
            0,
            _color_error_message_in_red(
                '_update_loop() should exit immediately and never call message.edit() when duration is 0.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_update_loop_calls_message_edit(self) -> None:

        updater, message, _ = self._build_updater()
        message.edit        = AsyncMock(side_effect = [None, Exception("stop")])

        with (
            patch("Utils.Embed.Now_Playing_Updater.asyncio.sleep", new = AsyncMock()),
            patch("Utils.Embed.Now_Playing_Updater.build_now_playing_embed", return_value = (Mock(), None))
        ):
            await updater._update_loop()

        self.assertGreaterEqual(
            message.edit.call_count,
            1,
            _color_error_message_in_red(
                '_update_loop() should call message.edit() at least once when duration is set.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_update_loop_stops_when_edit_raises(self) -> None:

        updater, message, _ = self._build_updater()
        message.edit        = AsyncMock(side_effect = Exception("message deleted"))

        with (
            patch("Utils.Embed.Now_Playing_Updater.asyncio.sleep", new = AsyncMock()),
            patch("Utils.Embed.Now_Playing_Updater.build_now_playing_embed", return_value = (Mock(), None))
        ):
            await updater._update_loop()

        self.assertEqual(
            message.edit.call_count,
            1,
            _color_error_message_in_red(
                '_update_loop() should stop after the first edit failure and not retry.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_update_loop_uses_pause_icon_when_paused(self) -> None:

        updater, message, _ = self._build_updater(is_paused = True)
        message.edit        = AsyncMock(side_effect = [None, Exception("stop")])

        captured_bars: list = []

        def _mock_build(song, progress_bar: str = "", **kwargs) -> tuple:
            captured_bars.append(progress_bar)
            return Mock(), None

        with (
            patch("Utils.Embed.Now_Playing_Updater.asyncio.sleep", new = AsyncMock()),
            patch("Utils.Embed.Now_Playing_Updater.build_now_playing_embed", side_effect = _mock_build)
        ):
            await updater._update_loop()

        self.assertTrue(
            all("❚❚" in bar for bar in captured_bars),
            _color_error_message_in_red(
                '_update_loop() should use the ❚❚ pause icon in the progress bar while paused.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_update_loop_elapsed_accounts_for_seek_offset(self) -> None:

        # start_time=1000, loop.time()=1005, seek_offset=60 → elapsed = 1005 - 1000 - 0 + 60 = 65 → "1:05"
        message      = Mock(edit = AsyncMock(side_effect = [None, Exception("stop")]))
        voice_client = Mock(is_paused = Mock(return_value = False))
        song         = {"title": "Test Song", "duration": 300.0}
        updater      = Now_Playing_Updater(message, song, voice_client, start_time = 1000.0, seek_offset = 60)

        captured_bars: list = []

        def _mock_build(song, progress_bar: str = "", **kwargs) -> tuple:
            captured_bars.append(progress_bar)
            return Mock(), None

        mock_loop      = Mock()
        mock_loop.time = Mock(return_value = 1005.0)

        with (
            patch("Utils.Embed.Now_Playing_Updater.asyncio.sleep", new = AsyncMock()),
            patch("Utils.Embed.Now_Playing_Updater.asyncio.get_running_loop", return_value = mock_loop),
            patch("Utils.Embed.Now_Playing_Updater.build_now_playing_embed", side_effect = _mock_build)
        ):
            await updater._update_loop()

        self.assertIn(
            "1:05",
            captured_bars[0],
            _color_error_message_in_red(
                'With start_time=1000, loop.time()=1005, seek_offset=60 the elapsed is 65s → bar should show "1:05".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_update_loop_uses_play_icon_when_playing(self) -> None:

        updater, message, _ = self._build_updater(is_paused = False)
        message.edit        = AsyncMock(side_effect = [None, Exception("stop")])

        captured_bars: list = []

        def _mock_build(song, progress_bar: str = "", **kwargs) -> tuple:
            captured_bars.append(progress_bar)
            return Mock(), None

        with (
            patch("Utils.Embed.Now_Playing_Updater.asyncio.sleep", new = AsyncMock()),
            patch("Utils.Embed.Now_Playing_Updater.build_now_playing_embed", side_effect = _mock_build)
        ):
            await updater._update_loop()

        self.assertTrue(
            all("▶" in bar for bar in captured_bars),
            _color_error_message_in_red(
                '_update_loop() should use the ▶ play icon in the progress bar while playing.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
