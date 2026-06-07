###########################################################################################################################
#   Tests for build_song_item_from_youtube() in Utils/Song.                                                              #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Constants as CONST
from Utils.Song import build_song_item_from_youtube
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Build_Song_Item_From_Youtube(unittest.TestCase):

    def test_returns_song_item_with_all_correct_fields(self) -> None:

        video = {
            "webpage_url" : "https://youtube.com/watch?v=abc",
            "title"       : "Test Song",
            "duration"    : 180
        }
        result = build_song_item_from_youtube(video, CONST.TESTING_AUTHOR_NAME)

        self.assertEqual(
            result["source_type"],
            "Youtube",
            _color_error_message_in_red(
                'source_type should be "Youtube".'
            )
        )
        self.assertEqual(
            result["title"],
            "Test Song",
            _color_error_message_in_red(
                'title should match the video title.'
            )
        )
        self.assertEqual(
            result["playback_query"],
            "https://youtube.com/watch?v=abc",
            _color_error_message_in_red(
                'playback_query should match webpage_url.'
            )
        )
        self.assertEqual(
            result["duration"],
            180,
            _color_error_message_in_red(
                'duration should match the video duration.'
            )
        )
        self.assertEqual(
            result["requested_by"],
            CONST.TESTING_AUTHOR_NAME,
            _color_error_message_in_red(
                'requested_by should match the provided author name.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_uses_id_as_fallback_when_webpage_url_is_missing(self) -> None:

        video = {
            "id"       : "abc123",
            "title"    : "Test Song",
            "duration" : 60
        }
        result = build_song_item_from_youtube(video, CONST.TESTING_AUTHOR_NAME)

        self.assertEqual(
            result["playback_query"],
            "abc123",
            _color_error_message_in_red(
                'playback_query should fall back to video id when webpage_url is absent.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_none_when_title_is_missing(self) -> None:

        video  = {"webpage_url": "https://youtube.com/watch?v=abc"}
        result = build_song_item_from_youtube(video, CONST.TESTING_AUTHOR_NAME)

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'build_song_item_from_youtube() should return None when title is missing.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_returns_none_when_both_url_and_id_are_missing(self) -> None:

        video  = {"title": "Test Song"}
        result = build_song_item_from_youtube(video, CONST.TESTING_AUTHOR_NAME)

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'build_song_item_from_youtube() should return None when both webpage_url and id are absent.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_duration_defaults_to_zero_when_missing(self) -> None:

        video  = {
            "webpage_url" : "https://youtube.com/watch?v=abc",
            "title"       : "Test Song"
        }
        result = build_song_item_from_youtube(video, CONST.TESTING_AUTHOR_NAME)

        self.assertEqual(
            result["duration"],
            0,
            _color_error_message_in_red(
                'duration should default to 0 when not present in the video payload.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
