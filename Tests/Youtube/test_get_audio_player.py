###########################################################################################################################
#   Tests for get_audio_player() in Utils/Youtube.                                                                       #
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

import Utils.Youtube
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Get_Audio_Player(unittest.TestCase):

    def test_get_audio_player_returns_player_on_success(self) -> None:

        """
        Test that get_audio_player() builds and returns a PCMVolumeTransformer on success.
        """

        raw_audio_url = "https://example.com/audio"
        fake_ffmpeg_audio = Mock()
        fake_player = Mock()

        with (
            patch("Utils.Youtube.FFmpegPCMAudio", return_value = fake_ffmpeg_audio) as mock_ffmpeg_audio,
            patch("Utils.Youtube.PCMVolumeTransformer", return_value = fake_player) as mock_volume_transformer
        ):
            result = Utils.Youtube.get_audio_player(raw_audio_url)

        self.assertIs(
            result,
            fake_player,
            _color_error_message_in_red(
                f'The "get_audio_player()" function should return "{fake_player}" instead of "{result}".'
            )
        )

        mock_ffmpeg_audio.assert_called_once_with(
            raw_audio_url,
            before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options        = "-vn"
        )

        mock_volume_transformer.assert_called_once_with(fake_ffmpeg_audio)

    #######################################################################################################################
    #######################################################################################################################

    def test_get_audio_player_with_start_offset_prepends_ss_flag(self) -> None:

        """
        Test that get_audio_player() prepends -ss <offset> to before_options when start_offset > 0.
        """

        raw_audio_url = "https://example.com/audio"
        fake_ffmpeg_audio = Mock()
        fake_player = Mock()

        with (
            patch("Utils.Youtube.FFmpegPCMAudio", return_value = fake_ffmpeg_audio) as mock_ffmpeg_audio,
            patch("Utils.Youtube.PCMVolumeTransformer", return_value = fake_player)
        ):
            result = Utils.Youtube.get_audio_player(raw_audio_url, start_offset = 30)

        self.assertIs(
            result,
            fake_player,
            _color_error_message_in_red(
                'get_audio_player() should still return a player when start_offset is set.'
            )
        )

        mock_ffmpeg_audio.assert_called_once_with(
            raw_audio_url,
            before_options = "-ss 30 -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options        = "-vn"
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_audio_player_returns_none_on_error(self) -> None:

        """
        Test that get_audio_player() returns None when FFmpegPCMAudio raises an exception.
        """

        raw_audio_url = "https://example.com/audio"

        with (
            patch("Utils.Youtube.FFmpegPCMAudio", side_effect = Exception("ffmpeg error")),
            patch("Utils.Youtube.PCMVolumeTransformer"),
            patch("Utils.Youtube.print") as mock_print,
            patch("Utils.Youtube.save_exception_to_txt") as mock_save_exception
        ):
            result = Utils.Youtube.get_audio_player(raw_audio_url)

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "get_audio_player()" function should return "None" instead of "{result}" when an error is raised.'
            )
        )

        self.assertEqual(
            mock_print.call_count,
            1,
            _color_error_message_in_red(
                'Exactly ONE warning logging message should have been printed in terminal.'
            )
        )

        self.assertEqual(
            mock_save_exception.call_count,
            1,
            _color_error_message_in_red(
                'get_audio_player() should call save_exception_to_txt() exactly once on error.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)