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
from unittest.mock import Mock, patch, call

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Lyrics import fetch_lyrics
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_SYNCED_LRC = "[00:10.00]Line one\n[00:20.00]Line two"

def _make_response(status_code: int, json_data: object) -> Mock:
    """Build a mock requests.Response."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data
    return response

###########################################################################################################################
###########################################################################################################################

class Test_Fetch_Lyrics(unittest.TestCase):

    def test_empty_title_returns_none(self) -> None:

        result = fetch_lyrics(title = "", artists = "Queen", duration = 354)

        self.assertIsNone(
            result,
            _color_error_message_in_red("Empty title should return None without making any HTTP request")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_direct_get_200_with_synced_lyrics_returns_parsed_lyrics(self, mock_get: Mock) -> None:

        mock_get.return_value = _make_response(200, {"syncedLyrics": _SYNCED_LRC, "instrumental": False})

        result = fetch_lyrics(title = "Bohemian Rhapsody", artists = "Queen", duration = 354)

        self.assertIsNotNone(
            result,
            _color_error_message_in_red("200 response with synced lyrics should return parsed list")
        )
        self.assertEqual(
            len(result),
            2,
            _color_error_message_in_red("Should parse exactly 2 lyric lines from sample LRC")
        )
        # Verify only the /get endpoint was called, not /search
        self.assertEqual(
            mock_get.call_count,
            1,
            _color_error_message_in_red("Should make exactly one HTTP call when /get succeeds")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_direct_get_200_instrumental_returns_none(self, mock_get: Mock) -> None:

        mock_get.return_value = _make_response(200, {"syncedLyrics": _SYNCED_LRC, "instrumental": True})

        result = fetch_lyrics(title = "Clair de Lune", artists = "Debussy", duration = 300)

        self.assertIsNone(
            result,
            _color_error_message_in_red("Instrumental track should return None")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_direct_get_200_no_synced_lyrics_returns_none_without_search(self, mock_get: Mock) -> None:

        mock_get.return_value = _make_response(200, {"syncedLyrics": None, "instrumental": False})

        result = fetch_lyrics(title = "Some Song", artists = "Artist", duration = 200)

        self.assertIsNone(
            result,
            _color_error_message_in_red("200 with no syncedLyrics should return None and not fall through to search")
        )
        self.assertEqual(
            mock_get.call_count,
            1,
            _color_error_message_in_red("Should not call /search when /get found the track but has no synced lyrics")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.save_exception_to_txt")
    @patch("Utils.Lyrics.requests.get")
    def test_direct_get_exception_saves_log_and_returns_none(self, mock_get: Mock, mock_save: Mock) -> None:

        mock_get.side_effect = Exception("Connection refused")

        result = fetch_lyrics(title = "Song", artists = "Artist", duration = 200)

        self.assertIsNone(
            result,
            _color_error_message_in_red("Exception from /get should return None")
        )
        mock_save.assert_called_once()
        self.assertEqual(
            mock_save.call_args.kwargs.get("title"),
            "Lyrics_Fetch_Direct",
            _color_error_message_in_red("Exception log title should be 'Lyrics_Fetch_Direct'")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_direct_get_404_falls_through_to_search(self, mock_get: Mock) -> None:

        # /get returns 404, /search returns results with synced lyrics
        mock_get.side_effect = [
            _make_response(404, {}),
            _make_response(200, [{"syncedLyrics": _SYNCED_LRC, "instrumental": False}]),
        ]

        result = fetch_lyrics(title = "Rare Song", artists = "Artist", duration = 200)

        self.assertIsNotNone(
            result,
            _color_error_message_in_red("404 from /get should fall through to search and find lyrics")
        )
        self.assertEqual(
            mock_get.call_count,
            2,
            _color_error_message_in_red("Should call both /get and /search when /get returns 404")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_no_artist_skips_direct_and_uses_search(self, mock_get: Mock) -> None:

        mock_get.return_value = _make_response(
            200,
            [{"syncedLyrics": _SYNCED_LRC, "instrumental": False}]
        )

        result = fetch_lyrics(title = "Bohemian Rhapsody", artists = "", duration = 0)

        self.assertIsNotNone(
            result,
            _color_error_message_in_red("No-artist case should use /search and return lyrics when found")
        )
        # Verify the URL was the /search endpoint
        called_url = mock_get.call_args.kwargs.get("url") or mock_get.call_args.args[0]
        self.assertIn(
            "/search",
            called_url,
            _color_error_message_in_red("No-artist case should call /search, not /get")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_search_200_no_synced_in_any_result_returns_none(self, mock_get: Mock) -> None:

        mock_get.return_value = _make_response(
            200,
            [
                {"syncedLyrics": None, "instrumental": False},
                {"syncedLyrics": "",   "instrumental": False},
            ]
        )

        result = fetch_lyrics(title = "Song", artists = "", duration = 0)

        self.assertIsNone(
            result,
            _color_error_message_in_red("Search results with no synced lyrics should return None")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_search_non_200_response_returns_none(self, mock_get: Mock) -> None:

        mock_get.return_value = _make_response(500, {})

        result = fetch_lyrics(title = "Song", artists = "", duration = 0)

        self.assertIsNone(
            result,
            _color_error_message_in_red("Non-200 search response should return None")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.save_exception_to_txt")
    @patch("Utils.Lyrics.requests.get")
    def test_search_exception_saves_log_and_returns_none(self, mock_get: Mock, mock_save: Mock) -> None:

        mock_get.side_effect = Exception("Timeout")

        result = fetch_lyrics(title = "Song", artists = "", duration = 0)

        self.assertIsNone(
            result,
            _color_error_message_in_red("Exception from /search should return None")
        )
        mock_save.assert_called_once()
        self.assertEqual(
            mock_save.call_args.kwargs.get("title"),
            "Lyrics_Fetch_Search",
            _color_error_message_in_red("Exception log title should be 'Lyrics_Fetch_Search'")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_title_noise_official_video_is_stripped(self, mock_get: Mock) -> None:

        mock_get.return_value = _make_response(200, [])

        fetch_lyrics(title = "Bohemian Rhapsody (Official Video)", artists = "", duration = 0)

        called_params = mock_get.call_args.kwargs.get("params") or {}
        self.assertEqual(
            called_params.get("track_name"),
            "Bohemian Rhapsody",
            _color_error_message_in_red("'(Official Video)' noise should be stripped before querying")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_title_noise_letra_is_stripped(self, mock_get: Mock) -> None:

        mock_get.return_value = _make_response(200, [])

        fetch_lyrics(title = "La bebecita bebe lean (Letra)", artists = "", duration = 0)

        called_params = mock_get.call_args.kwargs.get("params") or {}
        self.assertEqual(
            called_params.get("track_name"),
            "La bebecita bebe lean",
            _color_error_message_in_red("'(Letra)' Spanish lyric-video noise should be stripped before querying")
        )

    ###################################################################################################################

    @patch("Utils.Lyrics.requests.get")
    def test_search_returns_first_result_with_synced_lyrics(self, mock_get: Mock) -> None:

        # First result has no synced, second has synced
        mock_get.return_value = _make_response(
            200,
            [
                {"syncedLyrics": None,        "instrumental": False},
                {"syncedLyrics": _SYNCED_LRC, "instrumental": False},
                {"syncedLyrics": "[00:05.00]Third result", "instrumental": False},
            ]
        )

        result = fetch_lyrics(title = "Song", artists = "", duration = 0)

        self.assertIsNotNone(
            result,
            _color_error_message_in_red("Should return the first result that has synced lyrics")
        )
        self.assertEqual(
            len(result),
            2,
            _color_error_message_in_red("Should parse lyrics from the second result (first with synced), not the third")
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main()
