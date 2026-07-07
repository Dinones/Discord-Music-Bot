###########################################################################################################################
#   Tests for Music_Manager.prepare_seek_player().                                                                        #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Prepare_Seek_Player(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_false_when_current_song_is_none(self) -> None:

        self.manager.current_song = None

        result = await self.manager.prepare_seek_player(60)

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'prepare_seek_player() should return False when current_song is None.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_false_when_stream_url_is_missing(self) -> None:

        self.manager.current_song = {"title": "Test Song"}

        result = await self.manager.prepare_seek_player(60)

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'prepare_seek_player() should return False when _stream_url is not in current_song.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_false_when_stream_url_is_empty(self) -> None:

        self.manager.current_song = {"title": "Test Song", "_stream_url": ""}

        result = await self.manager.prepare_seek_player(60)

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'prepare_seek_player() should return False when _stream_url is an empty string.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_false_when_player_creation_fails(self) -> None:

        self.manager.current_song = {"title": "Test Song", "_stream_url": "https://stream.url"}

        with patch("Utils.Music_Manager.get_audio_player", return_value = None):
            result = await self.manager.prepare_seek_player(60)

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'prepare_seek_player() should return False when get_audio_player() returns None.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_prefetched_seek_player_is_none_when_player_creation_fails(self) -> None:

        self.manager.current_song = {"title": "Test Song", "_stream_url": "https://stream.url"}

        with patch("Utils.Music_Manager.get_audio_player", return_value = None):
            await self.manager.prepare_seek_player(60)

        self.assertIsNone(
            self.manager.prefetched_seek_player,
            _color_error_message_in_red(
                'prefetched_seek_player should remain None when player creation fails.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_false_when_player_warm_fails(self) -> None:

        self.manager.current_song = {"title": "Test Song", "_stream_url": "https://stream.url"}

        mock_player       = Mock()
        mock_player.read  = Mock(return_value = None)

        with patch("Utils.Music_Manager.get_audio_player", return_value = mock_player):
            result = await self.manager.prepare_seek_player(60)

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'prepare_seek_player() should return False when player.read() returns a falsy value (EOF before first frame).'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_true_on_success(self) -> None:

        self.manager.current_song = {"title": "Test Song", "_stream_url": "https://stream.url"}

        mock_player       = Mock()
        mock_player.read  = Mock(return_value = b"pcm_frame_data")

        with patch("Utils.Music_Manager.get_audio_player", return_value = mock_player):
            result = await self.manager.prepare_seek_player(60)

        self.assertTrue(
            result,
            _color_error_message_in_red(
                'prepare_seek_player() should return True when the player is successfully built and warmed.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_stores_player_in_prefetched_seek_player_on_success(self) -> None:

        self.manager.current_song = {"title": "Test Song", "_stream_url": "https://stream.url"}

        mock_player       = Mock()
        mock_player.read  = Mock(return_value = b"pcm_frame_data")

        with patch("Utils.Music_Manager.get_audio_player", return_value = mock_player):
            await self.manager.prepare_seek_player(60)

        self.assertIsNotNone(
            self.manager.prefetched_seek_player,
            _color_error_message_in_red(
                'prepare_seek_player() should store the pre-warmed player in prefetched_seek_player on success.'
            )
        )

        stored_player, _ = self.manager.prefetched_seek_player

        self.assertIs(
            stored_player,
            mock_player,
            _color_error_message_in_red(
                'The stored player should be the same object returned by get_audio_player().'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_stores_correct_seek_offset_in_prefetched_player(self) -> None:

        self.manager.current_song = {"title": "Test Song", "_stream_url": "https://stream.url"}

        mock_player       = Mock()
        mock_player.read  = Mock(return_value = b"pcm_frame_data")

        with patch("Utils.Music_Manager.get_audio_player", return_value = mock_player):
            await self.manager.prepare_seek_player(90)

        _, stored_seek_to = self.manager.prefetched_seek_player

        self.assertEqual(
            stored_seek_to,
            90,
            _color_error_message_in_red(
                'The seek offset stored in prefetched_seek_player should match the seek_to argument (90).'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_passes_seek_offset_to_audio_player(self) -> None:

        self.manager.current_song = {"title": "Test Song", "_stream_url": "https://stream.url"}

        mock_player       = Mock()
        mock_player.read  = Mock(return_value = b"pcm_frame_data")

        with patch("Utils.Music_Manager.get_audio_player", return_value = mock_player) as mock_get:
            await self.manager.prepare_seek_player(45)

        mock_get.assert_called_once_with(
            "https://stream.url",
            start_offset = 45
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_overwrites_existing_prefetched_seek_player_on_success(self) -> None:

        self.manager.current_song           = {"title": "Test Song", "_stream_url": "https://stream.url"}
        self.manager.prefetched_seek_player = (Mock(), 0)

        mock_player       = Mock()
        mock_player.read  = Mock(return_value = b"pcm_frame_data")

        with patch("Utils.Music_Manager.get_audio_player", return_value = mock_player):
            await self.manager.prepare_seek_player(120)

        _, stored_seek_to = self.manager.prefetched_seek_player

        self.assertEqual(
            stored_seek_to,
            120,
            _color_error_message_in_red(
                'prepare_seek_player() should overwrite any previously stored prefetched_seek_player.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
