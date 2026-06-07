###########################################################################################################################
#   Tests for the on_voice_state_update event handler in Main.                                                           #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Main import _build_bot, Bot_Runtime_Config
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_On_Voice_State_Update(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        with patch("Utils.Music_Manager.configure_ytdl"):
            from Utils.Music_Manager import Music_Manager
            self.music_manager = Music_Manager()

        config = Bot_Runtime_Config(
            env                  = "dev",
            discord_server_name  = "",
            activity             = None,
            discord_text_channel = None
        )
        bot                  = _build_bot(config)
        self.event_handler   = bot.on_voice_state_update

    #######################################################################################################################
    #######################################################################################################################

    def _build_human_member(self, guild_voice_client: Mock = None) -> Mock:

        member              = Mock()
        member.bot          = False
        member.guild        = Mock()
        member.guild.voice_client = guild_voice_client

        return member

    #######################################################################################################################
    #######################################################################################################################

    def _build_voice_client(self, non_bot_members: list = None) -> Mock:

        bot_member     = Mock()
        bot_member.bot = True
        members        = (non_bot_members or []) + [bot_member]

        vc                    = Mock()
        vc.is_connected       = Mock(return_value = True)
        vc.channel            = Mock()
        vc.channel.members    = members

        return vc

    #######################################################################################################################
    #######################################################################################################################

    async def test_ignores_bot_member_voice_state_changes(self) -> None:

        bot_member     = Mock()
        bot_member.bot = True

        with patch("Main.get_music_manager", return_value = self.music_manager):
            await self.event_handler(bot_member, Mock(), Mock())

        self.assertIsNone(
            self.music_manager.alone_timeout_task,
            _color_error_message_in_red(
                'on_voice_state_update() should ignore voice state changes by bot accounts.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_does_nothing_when_bot_has_no_voice_client(self) -> None:

        member = self._build_human_member(guild_voice_client = None)

        with patch("Main.get_music_manager", return_value = self.music_manager):
            with patch("Main.asyncio.create_task") as mock_create_task:
                await self.event_handler(member, Mock(), Mock())

        mock_create_task.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_does_not_start_timer_when_humans_are_present(self) -> None:

        human     = Mock()
        human.bot = False
        vc        = self._build_voice_client(non_bot_members = [human])
        member    = self._build_human_member(guild_voice_client = vc)

        with patch("Main.get_music_manager", return_value = self.music_manager):
            with patch("Main.asyncio.create_task") as mock_create_task:
                await self.event_handler(member, Mock(), Mock())

        mock_create_task.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_starts_timer_when_bot_is_alone_in_channel(self) -> None:

        vc     = self._build_voice_client(non_bot_members = [])
        member = self._build_human_member(guild_voice_client = vc)

        def _sink_coro(coro: Any) -> Mock:
            coro.close()
            return Mock()

        with patch("Main.get_music_manager", return_value = self.music_manager):
            with patch("Main.asyncio.create_task", side_effect = _sink_coro) as mock_create_task:
                await self.event_handler(member, Mock(), Mock())

        mock_create_task.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_does_not_start_duplicate_timer_when_task_already_running(self) -> None:

        existing_task      = Mock()
        existing_task.done = Mock(return_value = False)
        self.music_manager.alone_timeout_task = existing_task

        vc     = self._build_voice_client(non_bot_members = [])
        member = self._build_human_member(guild_voice_client = vc)

        with patch("Main.get_music_manager", return_value = self.music_manager):
            with patch("Main.asyncio.create_task") as mock_create_task:
                await self.event_handler(member, Mock(), Mock())

        mock_create_task.assert_not_called()

    #######################################################################################################################
    #######################################################################################################################

    async def test_starts_new_timer_when_previous_task_is_done(self) -> None:

        done_task      = Mock()
        done_task.done = Mock(return_value = True)
        self.music_manager.alone_timeout_task = done_task

        vc     = self._build_voice_client(non_bot_members = [])
        member = self._build_human_member(guild_voice_client = vc)

        def _sink_coro(coro: Any) -> Mock:
            coro.close()
            return Mock()

        with patch("Main.get_music_manager", return_value = self.music_manager):
            with patch("Main.asyncio.create_task", side_effect = _sink_coro) as mock_create_task:
                await self.event_handler(member, Mock(), Mock())

        mock_create_task.assert_called_once()

    #######################################################################################################################
    #######################################################################################################################

    async def test_cancels_pending_timer_when_human_rejoins(self) -> None:

        pending_task      = Mock()
        pending_task.done = Mock(return_value = False)
        self.music_manager.alone_timeout_task = pending_task

        human     = Mock()
        human.bot = False
        vc        = self._build_voice_client(non_bot_members = [human])
        member    = self._build_human_member(guild_voice_client = vc)

        with patch("Main.get_music_manager", return_value = self.music_manager):
            await self.event_handler(member, Mock(), Mock())

        pending_task.cancel.assert_called_once()
        self.assertIsNone(
            self.music_manager.alone_timeout_task,
            _color_error_message_in_red(
                'on_voice_state_update() should set alone_timeout_task to None after cancelling it.'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
