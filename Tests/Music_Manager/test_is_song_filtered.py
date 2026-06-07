###########################################################################################################################
#   Tests for _is_song_filtered() in Music_Manager.                                                                      #
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

from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_FAKE_GENRE_FILTERS = {
    "Reggaeton": ["Bad Bunny", "J Balvin"],
    "Catalan":   ["Els Pets"],
}

###########################################################################################################################
###########################################################################################################################

class Test_Is_Song_Filtered(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_false_when_no_active_filters(self) -> None:

        result = self.manager._is_song_filtered({"spotify_authors": "Bad Bunny", "title": "Tití Me Preguntó"})

        self.assertFalse(
            result,
            _color_error_message_in_red(
                '_is_song_filtered() should return False when no filters are active.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_true_when_artist_in_spotify_authors_matches(self) -> None:

        self.manager.active_filters.add("Reggaeton")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = self.manager._is_song_filtered({"spotify_authors": "Bad Bunny", "title": "Song"})

        self.assertTrue(
            result,
            _color_error_message_in_red(
                '_is_song_filtered() should return True when spotify_authors contains a filtered artist.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_true_when_artist_in_title_matches(self) -> None:

        self.manager.active_filters.add("Reggaeton")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = self.manager._is_song_filtered({"spotify_authors": "", "title": "Bad Bunny - Tití Me Preguntó"})

        self.assertTrue(
            result,
            _color_error_message_in_red(
                '_is_song_filtered() should return True when the song title contains a filtered artist name.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_matching_is_case_insensitive(self) -> None:

        self.manager.active_filters.add("Reggaeton")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = self.manager._is_song_filtered({"spotify_authors": "bad bunny", "title": ""})

        self.assertTrue(
            result,
            _color_error_message_in_red(
                '_is_song_filtered() should match artist names case-insensitively.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_false_when_artist_not_in_active_filter(self) -> None:

        self.manager.active_filters.add("Reggaeton")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = self.manager._is_song_filtered({"spotify_authors": "Ed Sheeran", "title": "Shape of You"})

        self.assertFalse(
            result,
            _color_error_message_in_red(
                '_is_song_filtered() should return False when artist is not in any active filter list.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_false_when_genre_artist_list_is_empty(self) -> None:

        self.manager.active_filters.add("Catalan")

        with patch("Utils.Music_Manager.GENRE_FILTERS", {"Catalan": []}):
            result = self.manager._is_song_filtered({"spotify_authors": "Any Artist", "title": ""})

        self.assertFalse(
            result,
            _color_error_message_in_red(
                '_is_song_filtered() should return False when the active genre has an empty artist list.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_false_when_matching_artist_is_in_inactive_genre(self) -> None:

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = self.manager._is_song_filtered({"spotify_authors": "Bad Bunny", "title": ""})

        self.assertFalse(
            result,
            _color_error_message_in_red(
                '_is_song_filtered() should return False when the matching artist belongs to an inactive filter genre.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_true_when_only_one_of_multiple_active_genres_matches(self) -> None:

        self.manager.active_filters.add("Reggaeton")
        self.manager.active_filters.add("Catalan")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = self.manager._is_song_filtered({"spotify_authors": "Els Pets", "title": ""})

        self.assertTrue(
            result,
            _color_error_message_in_red(
                '_is_song_filtered() should return True when the artist matches any one of multiple active filters.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
