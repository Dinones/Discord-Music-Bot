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
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Tests.Helpers.helpers import _color_error_message_in_red
from Utils.Embed.Now_Playing import build_now_playing_embed

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Build_Now_Playing_Embed(unittest.TestCase):

    #######################################################################################################################
    #######################################################################################################################

    def _build(self, song: dict, **kwargs) -> object:
        with patch("Utils.Embed.Now_Playing.os.path.exists", return_value = False):
            return build_now_playing_embed(song, **kwargs)

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_title_uses_song_title(self) -> None:

        embed, _ = self._build({"title": "Blinding Lights"})

        self.assertEqual(
            embed.title,
            "Blinding Lights",
            _color_error_message_in_red(
                'build_now_playing_embed() should use the song title as the embed title.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_title_appends_spotify_authors(self) -> None:

        embed, _ = self._build({"title": "Blinding Lights", "spotify_authors": "The Weeknd"})

        self.assertIn(
            "The Weeknd",
            embed.title,
            _color_error_message_in_red(
                'build_now_playing_embed() should append spotify_authors to the embed title.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_title_strips_lyrics_keyword(self) -> None:

        embed, _ = self._build({"title": "Song lyrics"})

        self.assertNotIn(
            "lyrics",
            embed.title,
            _color_error_message_in_red(
                'build_now_playing_embed() should strip the word "lyrics" from the embed title.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_title_truncated_when_too_long(self) -> None:

        long_title = "A" * 60
        embed, _   = self._build({"title": long_title})

        self.assertTrue(
            embed.title.endswith("..."),
            _color_error_message_in_red(
                'build_now_playing_embed() should truncate titles longer than the max length with "...".'
            )
        )
        self.assertLessEqual(
            len(embed.title),
            52,
            _color_error_message_in_red(
                'build_now_playing_embed() should not exceed the maximum title length.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_url_uses_playback_query(self) -> None:

        url      = "https://www.youtube.com/watch?v=abc123"
        embed, _ = self._build({"title": "Song", "playback_query": url})

        self.assertEqual(
            embed.url,
            url,
            _color_error_message_in_red(
                'build_now_playing_embed() should use playback_query as the embed URL.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_url_falls_back_to_spotify_url(self) -> None:

        url      = "https://open.spotify.com/track/abc123"
        embed, _ = self._build({"title": "Song", "spotify_url": url})

        self.assertEqual(
            embed.url,
            url,
            _color_error_message_in_red(
                'build_now_playing_embed() should fall back to spotify_url when playback_query is absent.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_footer_contains_requested_by(self) -> None:

        embed, _ = self._build({"title": "Song", "requested_by": "Alice"})

        self.assertIn(
            "Alice",
            embed.footer.text,
            _color_error_message_in_red(
                'build_now_playing_embed() should include the requester name in the footer.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_has_timestamp(self) -> None:

        embed, _ = self._build({"title": "Song"})

        self.assertIsNotNone(
            embed.timestamp,
            _color_error_message_in_red(
                'build_now_playing_embed() should set a timestamp on the embed.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_file_is_none_when_disc_gif_path_not_configured(self) -> None:

        with patch("Utils.Embed.Now_Playing.CONST.EMBED_DISC_GIF_PATH", ""):
            _, embed_file = self._build({"title": "Song"})

        self.assertIsNone(
            embed_file,
            _color_error_message_in_red(
                'build_now_playing_embed() should return None for the file when EMBED_DISC_GIF_PATH is empty.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_file_is_none_when_disc_gif_file_missing(self) -> None:

        with (
            patch("Utils.Embed.Now_Playing.CONST.EMBED_DISC_GIF_PATH", "nonexistent/path.gif"),
            patch("Utils.Embed.Now_Playing.os.path.exists", return_value = False)
        ):
            _, embed_file = self._build({"title": "Song"})

        self.assertIsNone(
            embed_file,
            _color_error_message_in_red(
                'build_now_playing_embed() should return None for the file when the disc GIF file does not exist.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_description_set_when_progress_bar_provided(self) -> None:

        bar      = "▶⠀████░░░░░░░░░░░░░░░░⠀1:00 / 5:00"
        embed, _ = self._build({"title": "Song"}, progress_bar = bar)

        self.assertEqual(
            embed.description,
            bar,
            _color_error_message_in_red(
                'build_now_playing_embed() should set embed.description to the progress_bar string when provided.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_embed_description_empty_when_no_progress_bar(self) -> None:

        embed, _ = self._build({"title": "Song"})

        self.assertFalse(
            embed.description,
            _color_error_message_in_red(
                'build_now_playing_embed() should leave embed.description empty when no progress_bar is given.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
