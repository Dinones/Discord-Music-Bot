###########################################################################################################################
#   Tests for _build_player_for_song() in Music_Manager.                                                                 #
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

class Test_Build_Player_For_Song(unittest.TestCase):

    def setUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import _build_player_for_song
            self._build_player_for_song = _build_player_for_song

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_none_when_stream_url_is_empty_string(self) -> None:

        result = self._build_player_for_song({"title": "Test"}, {"url": ""})

        self.assertIsNone(
            result,
            _color_error_message_in_red("Empty stream URL should return None")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_none_when_url_key_is_missing(self) -> None:

        result = self._build_player_for_song({"title": "Test"}, {})

        self.assertIsNone(
            result,
            _color_error_message_in_red("Missing URL key in resolved_video should return None")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_none_when_player_creation_fails(self) -> None:

        with patch("Utils.Music_Manager.get_audio_player", return_value = None):
            result = self._build_player_for_song({"title": "Test"}, {"url": "https://audio.url"})

        self.assertIsNone(
            result,
            _color_error_message_in_red("None player from get_audio_player should return None")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_player_and_seek_offset_on_success(self) -> None:

        mock_player = Mock()
        song        = {"title": "Test", "seek_offset": 30}

        with (
            patch("Utils.Music_Manager.get_audio_player", return_value = mock_player),
            patch("Utils.Music_Manager.enrich_song_from_video")
        ):
            result = self._build_player_for_song(song, {"url": "https://audio.url"})

        self.assertIsNotNone(
            result,
            _color_error_message_in_red("Valid inputs should return a (player, seek_offset) tuple")
        )

        player, seek_offset = result

        self.assertEqual(
            player,
            mock_player,
            _color_error_message_in_red("Returned player should be the one from get_audio_player")
        )
        self.assertEqual(
            seek_offset,
            30,
            _color_error_message_in_red("Returned seek_offset should equal the value from the song")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_seek_offset_is_consumed_from_song(self) -> None:

        song = {"title": "Test", "seek_offset": 45}

        with (
            patch("Utils.Music_Manager.get_audio_player", return_value = Mock()),
            patch("Utils.Music_Manager.enrich_song_from_video")
        ):
            self._build_player_for_song(song, {"url": "https://audio.url"})

        self.assertNotIn(
            "seek_offset",
            song,
            _color_error_message_in_red("seek_offset should be popped from the song dict after being consumed")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_seek_offset_defaults_to_zero_when_absent(self) -> None:

        song = {"title": "Test"}

        with (
            patch("Utils.Music_Manager.get_audio_player", return_value = Mock()),
            patch("Utils.Music_Manager.enrich_song_from_video")
        ):
            _, seek_offset = self._build_player_for_song(song, {"url": "https://audio.url"})

        self.assertEqual(
            seek_offset,
            0,
            _color_error_message_in_red("seek_offset should default to 0 when not present in the song dict")
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_seek_offset_is_passed_to_audio_player(self) -> None:

        song = {"title": "Test", "seek_offset": 45}

        with (
            patch("Utils.Music_Manager.get_audio_player", return_value = Mock()) as mock_get,
            patch("Utils.Music_Manager.enrich_song_from_video")
        ):
            self._build_player_for_song(song, {"url": "https://audio.url"})

        mock_get.assert_called_once_with(
            "https://audio.url",
            start_offset = 45
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_song_is_enriched_from_resolved_video(self) -> None:

        song           = {"title": "Test"}
        resolved_video = {"url": "https://audio.url", "duration": 200}

        with (
            patch("Utils.Music_Manager.get_audio_player", return_value = Mock()),
            patch("Utils.Music_Manager.enrich_song_from_video") as mock_enrich
        ):
            self._build_player_for_song(song, resolved_video)

        mock_enrich.assert_called_once_with(
            song,
            resolved_video
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
