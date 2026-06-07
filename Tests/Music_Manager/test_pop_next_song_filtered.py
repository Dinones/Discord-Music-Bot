###########################################################################################################################
#   Tests for Music_Manager.pop_next_song_filtered().                                                                    #
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

_FAKE_GENRE_FILTERS = {"Reggaeton": ["Bad Bunny"]}

###########################################################################################################################
###########################################################################################################################

class Test_Pop_Next_Song_Filtered(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.manager = Music_Manager()

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_none_when_all_queues_empty(self) -> None:

        result = await self.manager.pop_next_song_filtered()

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'pop_next_song_filtered() should return None when both queues are empty.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_priority_song_is_returned_even_when_it_matches_active_filter(self) -> None:

        filtered_song = {"title": "Filtered", "spotify_authors": "Bad Bunny"}
        self.manager.priority_queue.append(filtered_song)
        self.manager.active_filters.add("Reggaeton")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = await self.manager.pop_next_song_filtered()

        self.assertEqual(
            result,
            filtered_song,
            _color_error_message_in_red(
                'pop_next_song_filtered() should bypass filters for the priority queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_filtered_normal_song_is_discarded_and_next_valid_song_returned(self) -> None:

        filtered_song = {"title": "Filtered", "spotify_authors": "Bad Bunny"}
        valid_song    = {"title": "Valid",    "spotify_authors": "Ed Sheeran"}
        self.manager.queue.append(filtered_song)
        self.manager.queue.append(valid_song)
        self.manager.active_filters.add("Reggaeton")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = await self.manager.pop_next_song_filtered()

        self.assertEqual(
            result,
            valid_song,
            _color_error_message_in_red(
                'pop_next_song_filtered() should skip the filtered song and return the next valid one.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_none_when_all_normal_songs_are_filtered(self) -> None:

        self.manager.queue.append({"title": "Song 1", "spotify_authors": "Bad Bunny"})
        self.manager.queue.append({"title": "Song 2", "spotify_authors": "Bad Bunny"})
        self.manager.active_filters.add("Reggaeton")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = await self.manager.pop_next_song_filtered()

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                'pop_next_song_filtered() should return None when every normal queue song is filtered.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_filtered_song_is_removed_from_queue(self) -> None:

        self.manager.queue.append({"title": "Filtered", "spotify_authors": "Bad Bunny"})
        self.manager.active_filters.add("Reggaeton")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            await self.manager.pop_next_song_filtered()

        self.assertEqual(
            len(self.manager.queue),
            0,
            _color_error_message_in_red(
                'A discarded filtered song should be removed from the normal queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sets_current_song_to_returned_song(self) -> None:

        valid_song = {"title": "Valid", "spotify_authors": "Ed Sheeran"}
        self.manager.queue.append(valid_song)

        result = await self.manager.pop_next_song_filtered()

        self.assertEqual(
            self.manager.current_song,
            valid_song,
            _color_error_message_in_red(
                'pop_next_song_filtered() should set current_song to the returned song.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_unfiltered_normal_song_is_returned_when_filter_active(self) -> None:

        valid_song = {"title": "Valid", "spotify_authors": "Ed Sheeran"}
        self.manager.queue.append(valid_song)
        self.manager.active_filters.add("Reggaeton")

        with patch("Utils.Music_Manager.GENRE_FILTERS", _FAKE_GENRE_FILTERS):
            result = await self.manager.pop_next_song_filtered()

        self.assertEqual(
            result,
            valid_song,
            _color_error_message_in_red(
                'pop_next_song_filtered() should return a normal song whose artist is not in any active filter.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_normal_song_when_no_filters_active(self) -> None:

        song = {"title": "Any Song", "spotify_authors": "Bad Bunny"}
        self.manager.queue.append(song)

        result = await self.manager.pop_next_song_filtered()

        self.assertEqual(
            result,
            song,
            _color_error_message_in_red(
                'pop_next_song_filtered() should behave like pop_next_song() when no filters are active.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
