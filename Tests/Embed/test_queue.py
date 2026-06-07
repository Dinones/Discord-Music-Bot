###########################################################################################################################
#   Tests for the queue embed builder in Embed/Queue.                                                                    #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Tests.Helpers.helpers import _color_error_message_in_red
from Utils.Embed.Queue import build_queue_embed

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Build_Queue_Embed(unittest.TestCase):

    #######################################################################################################################
    #######################################################################################################################

    def test_now_playing_field_added_when_current_song_present(self) -> None:

        embed       = build_queue_embed({"title": "My Song"}, [], [])
        field_names = [f.name for f in embed.fields]

        self.assertTrue(
            any("Now Playing" in name for name in field_names),
            _color_error_message_in_red(
                'build_queue_embed() should add a "Now Playing" field when a current song is provided.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_now_playing_field_contains_song_title(self) -> None:

        embed             = build_queue_embed({"title": "Awesome Track"}, [], [])
        now_playing_field = next(f for f in embed.fields if "Now Playing" in f.name)

        self.assertIn(
            "Awesome Track",
            now_playing_field.value,
            _color_error_message_in_red(
                'The "Now Playing" field value should contain the song title.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_priority_songs_shown_with_star_prefix(self) -> None:

        embed         = build_queue_embed(None, [{"title": "Priority Song"}], [])
        up_next_field = next(f for f in embed.fields if "Up Next" in f.name)

        self.assertIn(
            "✨",
            up_next_field.value,
            _color_error_message_in_red(
                'Priority songs should be prefixed with a ✨ in the "Up Next" field.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_normal_songs_shown_without_star_prefix(self) -> None:

        embed         = build_queue_embed(None, [], [{"title": "Normal Song"}])
        up_next_field = next(f for f in embed.fields if "Up Next" in f.name)

        self.assertNotIn(
            "⭐",
            up_next_field.value,
            _color_error_message_in_red(
                'Normal songs should not have a ⭐ prefix in the "Up Next" field.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_overflow_message_shown_when_more_than_max_songs(self) -> None:

        normal        = [{"title": f"Song {i}"} for i in range(20)]
        embed         = build_queue_embed(None, [], normal)
        up_next_field = next(f for f in embed.fields if "Up Next" in f.name)

        self.assertIn(
            "more song",
            up_next_field.value,
            _color_error_message_in_red(
                'build_queue_embed() should show an overflow message when more than _MAX_SONGS songs are in the queue.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_footer_contains_correct_song_count(self) -> None:

        embed = build_queue_embed(None, [], [{"title": "A"}, {"title": "B"}])

        self.assertIn(
            "2",
            embed.footer.text,
            _color_error_message_in_red(
                'The embed footer should include the total song count.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_up_next_field_exists(self) -> None:

        embed       = build_queue_embed(None, [], [{"title": "X"}, {"title": "Y"}])
        field_names = [f.name for f in embed.fields]

        self.assertTrue(
            any("Up Next" in name for name in field_names),
            _color_error_message_in_red(
                'build_queue_embed() should add an "Up Next" field when songs are queued.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
