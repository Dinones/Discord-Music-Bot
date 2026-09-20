###########################################################################################################################
#   Tests for pick_random_intro() in Utils/Audio_Intro.                                                                   #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Audio_Intro
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Pick_Random_Intro(unittest.TestCase):

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_none_when_playable_directory_does_not_exist(self) -> None:

        with patch("Utils.Audio_Intro.os.path.isdir", return_value = False):
            result = Utils.Audio_Intro.pick_random_intro()

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'pick_random_intro() should return None when the Playable directory does not exist.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_none_when_directory_contains_no_mp3_files(self) -> None:

        with (
            patch("Utils.Audio_Intro.os.path.isdir", return_value = True),
            patch("Utils.Audio_Intro.os.listdir",    return_value = ["readme.txt", "image.png"]),
        ):
            result = Utils.Audio_Intro.pick_random_intro()

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'pick_random_intro() should return None when no MP3 files are found in the Playable directory.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_none_when_directory_is_empty(self) -> None:

        with (
            patch("Utils.Audio_Intro.os.path.isdir", return_value = True),
            patch("Utils.Audio_Intro.os.listdir",    return_value = []),
        ):
            result = Utils.Audio_Intro.pick_random_intro()

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'pick_random_intro() should return None when the Playable directory is empty.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_path_ending_in_mp3_when_files_exist(self) -> None:

        with (
            patch("Utils.Audio_Intro.os.path.isdir", return_value = True),
            patch("Utils.Audio_Intro.os.listdir",    return_value = ["intro.mp3"]),
        ):
            result = Utils.Audio_Intro.pick_random_intro()

        self.assertIsNotNone(result)
        self.assertTrue(
            result.lower().endswith(".mp3"),
            _color_error_message_in_red(
                f'pick_random_intro() should return a path ending in ".mp3" instead of "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returned_path_is_within_playable_directory(self) -> None:

        with (
            patch("Utils.Audio_Intro.os.path.isdir", return_value = True),
            patch("Utils.Audio_Intro.os.listdir",    return_value = ["intro.mp3"]),
        ):
            result = Utils.Audio_Intro.pick_random_intro()

        self.assertTrue(
            result.startswith(Utils.Audio_Intro._PLAYABLE_DIR),
            _color_error_message_in_red(
                f'pick_random_intro() should return a path inside the Playable directory '
                f'("{Utils.Audio_Intro._PLAYABLE_DIR}"), got "{result}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_uses_random_choice_to_select_file(self) -> None:

        fake_files = ["a.mp3", "b.mp3", "c.mp3"]
        expected_paths = [
            os.path.join(Utils.Audio_Intro._PLAYABLE_DIR, f) for f in fake_files
        ]

        with (
            patch("Utils.Audio_Intro.os.path.isdir", return_value = True),
            patch("Utils.Audio_Intro.os.listdir",    return_value = fake_files),
            patch("Utils.Audio_Intro.random.choice", return_value = expected_paths[1]) as mock_choice,
        ):
            result = Utils.Audio_Intro.pick_random_intro()

        mock_choice.assert_called_once_with(expected_paths)
        self.assertEqual(
            result,
            expected_paths[1],
            _color_error_message_in_red(
                'pick_random_intro() should return the value chosen by random.choice().'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
