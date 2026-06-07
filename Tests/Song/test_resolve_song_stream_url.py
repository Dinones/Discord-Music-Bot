###########################################################################################################################
#   Tests for resolve_song_stream_url() in Utils/Song.                                                                   #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Song import resolve_song_stream_url
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Resolve_Song_Stream_Url(unittest.IsolatedAsyncioTestCase):

    def _build_context(self) -> Mock:

        context         = Mock()
        context.message = Mock()

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_spotify_song_returns_result_from_get_video_from_spotify_song(self) -> None:

        """
        Test that resolve_song_stream_url() calls get_video_from_spotify_song (via to_thread) for Spotify songs.
        """

        mock_video = {"title": "Found Video", "duration": 200}
        song       = {
            "source_type"    : "Spotify",
            "spotify_title"  : "My Song",
            "spotify_authors": "Artist A"
        }

        with (
            patch("Utils.Music_Manager.get_music_manager", return_value = Mock()),
            patch("Utils.Song.asyncio.to_thread", new = AsyncMock(return_value = mock_video)) as mock_thread
        ):
            result = await resolve_song_stream_url(self._build_context(), song)

        self.assertEqual(
            result,
            mock_video,
            _color_error_message_in_red(
                'resolve_song_stream_url() should return the video found by get_video_from_spotify_song.'
            )
        )

        self.assertEqual(
            mock_thread.call_count,
            1,
            _color_error_message_in_red(
                'resolve_song_stream_url() should call asyncio.to_thread() once for a Spotify song.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_spotify_song_with_empty_title_returns_none(self) -> None:

        """
        Test that resolve_song_stream_url() returns None when a Spotify song has no spotify_title.
        """

        song = {"source_type": "Spotify", "spotify_title": "", "spotify_authors": "Artist A"}

        with patch("Utils.Music_Manager.get_music_manager", return_value = Mock()):
            result = await resolve_song_stream_url(self._build_context(), song)

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'resolve_song_stream_url() should return None for a Spotify song with an empty spotify_title.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_youtube_song_calls_search_youtube_video(self) -> None:

        """
        Test that resolve_song_stream_url() calls search_youtube_video for YouTube songs.
        """

        mock_video = {"title": "Found Video", "duration": 180}
        song       = {"source_type": "Youtube", "playback_query": "https://youtube.com/watch?v=abc"}
        context    = self._build_context()

        with (
            patch("Utils.Music_Manager.get_music_manager", return_value = Mock()),
            patch("Utils.Song.search_youtube_video", new = AsyncMock(return_value = mock_video)) as mock_search
        ):
            result = await resolve_song_stream_url(context, song)

        self.assertEqual(
            result,
            mock_video,
            _color_error_message_in_red(
                'resolve_song_stream_url() should return the video found by search_youtube_video.'
            )
        )

        self.assertEqual(
            mock_search.call_count,
            1,
            _color_error_message_in_red(
                'resolve_song_stream_url() should call search_youtube_video() once for a YouTube song.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_youtube_song_with_empty_playback_query_returns_none(self) -> None:

        """
        Test that resolve_song_stream_url() returns None when a YouTube song has no playback_query.
        """

        song = {"source_type": "Youtube", "playback_query": ""}

        with patch("Utils.Music_Manager.get_music_manager", return_value = Mock()):
            result = await resolve_song_stream_url(self._build_context(), song)

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'resolve_song_stream_url() should return None for a YouTube song with an empty playback_query.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_youtube_song_with_missing_playback_query_returns_none(self) -> None:

        """
        Test that resolve_song_stream_url() returns None when a YouTube song has no playback_query key.
        """

        song = {"source_type": "Youtube"}

        with patch("Utils.Music_Manager.get_music_manager", return_value = Mock()):
            result = await resolve_song_stream_url(self._build_context(), song)

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'resolve_song_stream_url() should return None for a YouTube song missing playback_query.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
