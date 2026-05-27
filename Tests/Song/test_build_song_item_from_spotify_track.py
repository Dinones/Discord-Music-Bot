###########################################################################################################################
#                                                                                                                         #
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
from Utils.Song import build_song_item_from_spotify_track
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Build_Song_Item_From_Spotify_Track(unittest.TestCase):

    def test_returns_song_item_with_all_correct_fields(self) -> None:

        track = {
            "name"    : "Test Song",
            "artists" : [{"name": "Artist A"}, {"name": "Artist B"}]
        }
        result = build_song_item_from_spotify_track(track, CONST.TESTING_AUTHOR_NAME)

        self.assertEqual(
            result["source_type"],
            "Spotify",
            _color_error_message_in_red(
                'source_type should be "Spotify".'
            )
        )
        self.assertEqual(
            result["title"],
            "Test Song",
            _color_error_message_in_red(
                'title should match the track name.'
            )
        )
        self.assertEqual(
            result["spotify_title"],
            "Test Song",
            _color_error_message_in_red(
                'spotify_title should match the track name.'
            )
        )
        self.assertEqual(
            result["spotify_authors"],
            "Artist A, Artist B",
            _color_error_message_in_red(
                'spotify_authors should be a comma-separated list of artist names.'
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

    def test_returns_none_when_track_name_is_missing(self) -> None:

        track  = {"artists": [{"name": "Artist A"}]}
        result = build_song_item_from_spotify_track(track, CONST.TESTING_AUTHOR_NAME)

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'build_song_item_from_spotify_track() should return None when track name is missing.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_handles_single_artist(self) -> None:

        track = {
            "name"    : "Solo Song",
            "artists" : [{"name": "Solo Artist"}]
        }
        result = build_song_item_from_spotify_track(track, CONST.TESTING_AUTHOR_NAME)

        self.assertEqual(
            result["spotify_authors"],
            "Solo Artist",
            _color_error_message_in_red(
                'spotify_authors should contain the single artist name without a trailing comma.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_handles_empty_artists_list(self) -> None:

        track  = {"name": "Song", "artists": []}
        result = build_song_item_from_spotify_track(track, CONST.TESTING_AUTHOR_NAME)

        self.assertEqual(
            result["spotify_authors"],
            "",
            _color_error_message_in_red(
                'spotify_authors should be an empty string when no artists are provided.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_skips_artists_with_empty_names(self) -> None:

        track = {
            "name"    : "Song",
            "artists" : [{"name": ""}, {"name": "Real Artist"}]
        }
        result = build_song_item_from_spotify_track(track, CONST.TESTING_AUTHOR_NAME)

        self.assertEqual(
            result["spotify_authors"],
            "Real Artist",
            _color_error_message_in_red(
                'Artists with empty names should be excluded from spotify_authors.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
