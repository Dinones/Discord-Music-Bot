###########################################################################################################################
#   Tests for _collect_prefetch() in Music_Manager.                                                                      #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Collect_Prefetch(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import _collect_prefetch
            self._collect_prefetch = _collect_prefetch

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_none_when_no_prefetch_task(self) -> None:

        result = await self._collect_prefetch(None, {"title": "Song"})

        self.assertIsNone(
            result,
            _color_error_message_in_red("None prefetch_task should return None immediately")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_song_and_resolved_video_on_success(self) -> None:

        song           = {"title": "Next Song"}
        resolved_video = {"url": "https://audio.url"}

        future = asyncio.get_event_loop().create_future()
        future.set_result(resolved_video)

        result = await self._collect_prefetch(future, song)

        self.assertEqual(
            result,
            (song, resolved_video),
            _color_error_message_in_red("Should return (next_song, resolved_video) tuple on success")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_none_when_task_result_is_none(self) -> None:

        future = asyncio.get_event_loop().create_future()
        future.set_result(None)

        result = await self._collect_prefetch(future, {"title": "Song"})

        self.assertIsNone(
            result,
            _color_error_message_in_red("None task result should return None")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_none_and_logs_on_exception(self) -> None:

        future = asyncio.get_event_loop().create_future()
        future.set_exception(Exception("yt-dlp failed"))

        with (
            patch("Utils.Music_Manager.save_exception_to_txt") as mock_save,
            patch("Utils.Music_Manager.print")
        ):
            result = await self._collect_prefetch(future, {"title": "Song"})

        self.assertIsNone(
            result,
            _color_error_message_in_red("Exception in prefetch task should return None")
        )
        self.assertEqual(
            mock_save.call_count,
            1,
            _color_error_message_in_red("Exception should be logged via save_exception_to_txt")
        )
        self.assertEqual(
            mock_save.call_args.kwargs.get("title"),
            "Music_Manager_Prefetch",
            _color_error_message_in_red("Exception log title should be 'Music_Manager_Prefetch'")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_does_not_raise_on_exception(self) -> None:

        future = asyncio.get_event_loop().create_future()
        future.set_exception(RuntimeError("network error"))

        try:
            with (
                patch("Utils.Music_Manager.save_exception_to_txt"),
                patch("Utils.Music_Manager.print")
            ):
                await self._collect_prefetch(future, {"title": "Song"})
        except Exception as error:
            self.fail(
                _color_error_message_in_red(
                    f"_collect_prefetch() should not raise on task exception, but raised: {error}"
                )
            )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
