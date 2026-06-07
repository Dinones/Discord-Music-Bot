###########################################################################################################################
#   Tests for _resolve_stream() in Music_Manager.                                                                        #
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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Resolve_Stream(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import _resolve_stream
            self._resolve_stream = _resolve_stream

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_prefetched_result_when_song_matches(self) -> None:

        song       = {"title": "Song A", "duration": 200}
        cached     = {"url": "https://cached.url/audio"}
        prefetched = (song, cached)

        with patch("Utils.Music_Manager.resolve_song_stream_url", new = AsyncMock()) as mock_resolve:
            result = await self._resolve_stream(Mock(), song, prefetched)

        self.assertEqual(
            result,
            cached,
            _color_error_message_in_red("Should return the cached resolved_video when song reference matches prefetched")
        )
        mock_resolve.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_does_not_call_resolve_when_prefetch_matches(self) -> None:

        song       = {"title": "Song A"}
        cached     = {"url": "https://cached.url/audio"}
        prefetched = (song, cached)

        with patch("Utils.Music_Manager.resolve_song_stream_url", new = AsyncMock()) as mock_resolve:
            await self._resolve_stream(Mock(), song, prefetched)

        self.assertEqual(
            mock_resolve.call_count,
            0,
            _color_error_message_in_red("resolve_song_stream_url should not be called when pre-fetch matches")
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_fetches_fresh_when_prefetch_is_none(self) -> None:

        song    = {"title": "Song A", "duration": 200}
        fetched = {"url": "https://fresh.url/audio"}
        context = Mock()

        with patch("Utils.Music_Manager.resolve_song_stream_url", new = AsyncMock(return_value = fetched)) as mock_resolve:
            result = await self._resolve_stream(context, song, None)

        self.assertEqual(
            result,
            fetched,
            _color_error_message_in_red("Should return the freshly resolved video when prefetched is None")
        )
        mock_resolve.assert_called_once_with(context, song)

    #######################################################################################################################
    #######################################################################################################################

    async def test_fetches_fresh_when_different_song_in_prefetch(self) -> None:

        song_a     = {"title": "Song A"}
        song_b     = {"title": "Song B"}
        cached     = {"url": "https://cached.url/audio"}
        fetched    = {"url": "https://fresh.url/audio"}
        prefetched = (song_a, cached)

        with patch("Utils.Music_Manager.resolve_song_stream_url", new = AsyncMock(return_value = fetched)):
            result = await self._resolve_stream(Mock(), song_b, prefetched)

        self.assertEqual(
            result,
            fetched,
            _color_error_message_in_red("Should fetch fresh when prefetched song reference does not match current song")
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
