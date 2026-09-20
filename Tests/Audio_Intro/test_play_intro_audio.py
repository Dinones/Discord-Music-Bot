###########################################################################################################################
#   Tests for play_intro_audio() in Utils/Audio_Intro.                                                                    #
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

import Utils.Audio_Intro
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Play_Intro_Audio(unittest.IsolatedAsyncioTestCase):

    #######################################################################################################################
    #######################################################################################################################

    async def test_does_not_call_voice_client_play_when_no_intro_available(self) -> None:

        voice_client = Mock()

        with patch("Utils.Audio_Intro.pick_random_intro", return_value = None):
            await Utils.Audio_Intro.play_intro_audio(voice_client)

        voice_client.play.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_calls_voice_client_play_when_intro_is_available(self) -> None:

        voice_client = Mock()

        def fake_play(player, after):
            after(None)

        voice_client.play.side_effect = fake_play

        with (
            patch("Utils.Audio_Intro.pick_random_intro",      return_value = "/fake/intro.mp3"),
            patch("Utils.Audio_Intro.FFmpegPCMAudio",         return_value = Mock()),
            patch("Utils.Audio_Intro.PCMVolumeTransformer",   return_value = Mock()),
            patch("Utils.Audio_Intro.print"),
        ):
            await Utils.Audio_Intro.play_intro_audio(voice_client)

        voice_client.play.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_player_volume_is_set_to_1(self) -> None:

        voice_client = Mock()
        mock_player  = Mock()

        def fake_play(player, after):
            after(None)

        voice_client.play.side_effect = fake_play

        with (
            patch("Utils.Audio_Intro.pick_random_intro",    return_value = "/fake/intro.mp3"),
            patch("Utils.Audio_Intro.FFmpegPCMAudio",       return_value = Mock()),
            patch("Utils.Audio_Intro.PCMVolumeTransformer", return_value = mock_player),
            patch("Utils.Audio_Intro.print"),
        ):
            await Utils.Audio_Intro.play_intro_audio(voice_client)

        self.assertEqual(
            mock_player.volume,
            1.0,
            _color_error_message_in_red(
                f'play_intro_audio() should set player.volume to 1.0, got {mock_player.volume}.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_awaits_until_playback_finishes(self) -> None:

        voice_client  = Mock()
        call_log      = []

        def fake_play(player, after):
            after(None)

        voice_client.play.side_effect = fake_play

        with (
            patch("Utils.Audio_Intro.pick_random_intro",    return_value = "/fake/intro.mp3"),
            patch("Utils.Audio_Intro.FFmpegPCMAudio",       return_value = Mock()),
            patch("Utils.Audio_Intro.PCMVolumeTransformer", return_value = Mock()),
            patch("Utils.Audio_Intro.print"),
        ):
            await Utils.Audio_Intro.play_intro_audio(voice_client)
            call_log.append("returned")

        self.assertEqual(
            call_log,
            ["returned"],
            _color_error_message_in_red(
                'play_intro_audio() should return only after the after-callback fires.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
