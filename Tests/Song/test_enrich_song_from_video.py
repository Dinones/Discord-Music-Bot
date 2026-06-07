###########################################################################################################################
#   Tests for enrich_song_from_video() in Utils/Song.                                                                    #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Song import enrich_song_from_video
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Enrich_Song_From_Video(unittest.TestCase):

    def test_fills_playback_query_from_webpage_url(self) -> None:

        """
        Test that enrich_song_from_video() backfills playback_query from the video's webpage_url.
        """

        song  = {"source_type": "Spotify", "title": "Test", "requested_by": "user"}
        video = {"webpage_url": "https://youtube.com/watch?v=abc123", "duration": 200}

        enrich_song_from_video(song, video)

        self.assertEqual(
            song.get("playback_query"),
            "https://youtube.com/watch?v=abc123",
            _color_error_message_in_red(
                'enrich_song_from_video() should set playback_query from webpage_url.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_falls_back_to_id_when_webpage_url_missing(self) -> None:

        """
        Test that enrich_song_from_video() uses video id as playback_query fallback when webpage_url is absent.
        """

        song  = {"source_type": "Spotify", "title": "Test", "requested_by": "user"}
        video = {"id": "abc123", "duration": 200}

        enrich_song_from_video(song, video)

        self.assertEqual(
            song.get("playback_query"),
            "abc123",
            _color_error_message_in_red(
                'enrich_song_from_video() should fall back to video id when webpage_url is missing.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_does_not_overwrite_existing_playback_query(self) -> None:

        """
        Test that enrich_song_from_video() does not overwrite a playback_query that is already set.
        """

        song  = {"source_type": "Youtube", "title": "Test", "playback_query": "original_url", "requested_by": "user"}
        video = {"webpage_url": "https://youtube.com/watch?v=new", "duration": 200}

        enrich_song_from_video(song, video)

        self.assertEqual(
            song.get("playback_query"),
            "original_url",
            _color_error_message_in_red(
                'enrich_song_from_video() must not overwrite an existing playback_query.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_fills_duration_from_video(self) -> None:

        """
        Test that enrich_song_from_video() backfills duration from the resolved video payload.
        """

        song  = {"source_type": "Spotify", "title": "Test", "requested_by": "user"}
        video = {"webpage_url": "https://youtube.com/watch?v=abc", "duration": 240}

        enrich_song_from_video(song, video)

        self.assertEqual(
            song.get("duration"),
            240,
            _color_error_message_in_red(
                'enrich_song_from_video() should set duration from the resolved video payload.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_does_not_overwrite_existing_duration(self) -> None:

        """
        Test that enrich_song_from_video() does not overwrite a duration that is already set.
        """

        song  = {"source_type": "Youtube", "title": "Test", "playback_query": "url", "duration": 180, "requested_by": "user"}
        video = {"webpage_url": "https://youtube.com/watch?v=abc", "duration": 999}

        enrich_song_from_video(song, video)

        self.assertEqual(
            song.get("duration"),
            180,
            _color_error_message_in_red(
                'enrich_song_from_video() must not overwrite an existing duration.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_does_not_set_playback_query_when_video_has_no_url_or_id(self) -> None:

        """
        Test that enrich_song_from_video() does not set playback_query when the video has neither webpage_url nor id.
        """

        song  = {"source_type": "Spotify", "title": "Test", "requested_by": "user"}
        video = {"duration": 200}

        enrich_song_from_video(song, video)

        self.assertNotIn(
            "playback_query",
            song,
            _color_error_message_in_red(
                'enrich_song_from_video() should not set playback_query when the video has no URL or id.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_mutates_song_in_place_and_returns_none(self) -> None:

        """
        Test that enrich_song_from_video() mutates the song dict in-place and returns None.
        """

        song   = {"source_type": "Spotify", "title": "Test", "requested_by": "user"}
        video  = {"webpage_url": "https://youtube.com/watch?v=abc", "duration": 200}
        result = enrich_song_from_video(song, video)

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'enrich_song_from_video() should return None.'
            )
        )

        self.assertIn(
            "playback_query",
            song,
            _color_error_message_in_red(
                'enrich_song_from_video() should mutate the song dict in-place.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
