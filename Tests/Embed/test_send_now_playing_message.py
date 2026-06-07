###########################################################################################################################
#   Tests for _send_now_playing_message() in Now_Playing_Updater.                                                        #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Embed.Now_Playing_Updater import _send_now_playing_message
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Send_Now_Playing_Message(unittest.IsolatedAsyncioTestCase):

    def _build_context(self) -> Mock:

        context      = Mock()
        context.send = AsyncMock(return_value = Mock())

        return context

    #######################################################################################################################
    #######################################################################################################################

    async def test_returns_message_from_context_send(self) -> None:

        """
        Test that _send_now_playing_message() returns the message object produced by context.send().
        """

        mock_message = Mock()
        context      = self._build_context()
        context.send = AsyncMock(return_value = mock_message)
        song         = {"title": "Test Song", "duration": 0}

        with patch(
            "Utils.Embed.Now_Playing_Updater.build_now_playing_embed",
            return_value = (Mock(), None)
        ):
            result = await _send_now_playing_message(context, song)

        self.assertEqual(
            result,
            mock_message,
            _color_error_message_in_red(
                '_send_now_playing_message() should return the message object from context.send().'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_with_file_when_embed_file_is_present(self) -> None:

        """
        Test that _send_now_playing_message() passes file= to context.send() when build_now_playing_embed returns a file.
        """

        context    = self._build_context()
        song       = {"title": "Test Song", "duration": 0}
        mock_embed = Mock()
        mock_file  = Mock()

        with patch(
            "Utils.Embed.Now_Playing_Updater.build_now_playing_embed",
            return_value = (mock_embed, mock_file)
        ):
            await _send_now_playing_message(context, song)

        _, kwargs = context.send.call_args

        self.assertIn(
            "file",
            kwargs,
            _color_error_message_in_red(
                '_send_now_playing_message() should pass file= to context.send() when embed_file is not None.'
            )
        )
        self.assertEqual(
            kwargs["file"],
            mock_file,
            _color_error_message_in_red(
                '_send_now_playing_message() should pass the correct embed_file to context.send().'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_sends_without_file_when_embed_file_is_none(self) -> None:

        """
        Test that _send_now_playing_message() does not pass file= to context.send() when embed_file is None.
        """

        context    = self._build_context()
        song       = {"title": "Test Song", "duration": 0}
        mock_embed = Mock()

        with patch(
            "Utils.Embed.Now_Playing_Updater.build_now_playing_embed",
            return_value = (mock_embed, None)
        ):
            await _send_now_playing_message(context, song)

        _, kwargs = context.send.call_args

        self.assertNotIn(
            "file",
            kwargs,
            _color_error_message_in_red(
                '_send_now_playing_message() must not pass file= to context.send() when embed_file is None.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_passes_empty_progress_bar_when_duration_is_zero(self) -> None:

        """
        Test that _send_now_playing_message() passes an empty progress bar when duration is 0.
        """

        context         = self._build_context()
        song            = {"title": "Test Song", "duration": 0}
        captured_kwargs = {}

        def _capture_embed(song, progress_bar: str = "", **kwargs) -> tuple:
            captured_kwargs["progress_bar"] = progress_bar
            return Mock(), None

        with patch(
            "Utils.Embed.Now_Playing_Updater.build_now_playing_embed",
            side_effect = _capture_embed
        ):
            await _send_now_playing_message(context, song)

        self.assertEqual(
            captured_kwargs.get("progress_bar"),
            "",
            _color_error_message_in_red(
                '_send_now_playing_message() should pass an empty progress bar when duration is 0.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_passes_non_empty_progress_bar_when_duration_is_set(self) -> None:

        """
        Test that _send_now_playing_message() passes a non-empty progress bar when the song has a duration.
        """

        context         = self._build_context()
        song            = {"title": "Test Song", "duration": 300}
        captured_kwargs = {}

        def _capture_embed(song, progress_bar: str = "", **kwargs) -> tuple:
            captured_kwargs["progress_bar"] = progress_bar
            return Mock(), None

        with patch(
            "Utils.Embed.Now_Playing_Updater.build_now_playing_embed",
            side_effect = _capture_embed
        ):
            await _send_now_playing_message(context, song)

        self.assertNotEqual(
            captured_kwargs.get("progress_bar"),
            "",
            _color_error_message_in_red(
                '_send_now_playing_message() should pass a non-empty progress bar when duration is set.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_seek_offset_is_reflected_in_progress_bar(self) -> None:

        """
        Test that _send_now_playing_message() initialises the progress bar at the seek_offset position.
        """

        context         = self._build_context()
        song            = {"title": "Test Song", "duration": 300}
        captured_kwargs = {}

        def _capture_embed(song, progress_bar: str = "", **kwargs) -> tuple:
            captured_kwargs["progress_bar"] = progress_bar
            return Mock(), None

        with patch(
            "Utils.Embed.Now_Playing_Updater.build_now_playing_embed",
            side_effect = _capture_embed
        ):
            await _send_now_playing_message(context, song, seek_offset = 60)

        # 60 seconds into a 300s song should appear in the progress bar string (e.g. "1:00")
        self.assertIn(
            "1:00",
            captured_kwargs.get("progress_bar", ""),
            _color_error_message_in_red(
                '_send_now_playing_message() should reflect seek_offset in the initial progress bar.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
