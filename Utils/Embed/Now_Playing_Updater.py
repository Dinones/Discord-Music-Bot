###########################################################################################################################
#   Builds and live-updates the Now Playing embed with a progress bar and current lyric line.                            #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
import discord
from typing import Any, List, Optional, Tuple
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Song import Song_Item
from Utils.Embed.Now_Playing import build_now_playing_embed
from Utils.Lyrics import get_current_lyric_line

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

# Seconds between embed edits (~1 update per 5 s keeps well within Discord's rate limits)
_UPDATE_INTERVAL   = 1
_PROGRESS_BAR_WIDTH = 20

###########################################################################################################################
###########################################################################################################################

class Now_Playing_View(discord.ui.View):

    """
    Discord UI view attached to the Now Playing embed. Provides ⏪ / ⏸️▶️ / ⏩ control buttons.
    """

    def __init__(
        self,
        voice_client  : discord.VoiceClient,
        music_manager : Any,
    ) -> None:

        """
        Initialise the view and register the three control buttons.

        Args:
            voice_client (discord.VoiceClient): Active voice connection used to control playback.
            music_manager (Any): Global Music_Manager instance used to navigate the played history.

        Returns:
            None
        """

        super().__init__(timeout = None)

        self._voice_client  = voice_client
        self._music_manager = music_manager

        prev_btn          = discord.ui.Button(
            emoji     = "⏪",
            style     = discord.ButtonStyle.secondary,
            custom_id = "now_playing_prev",
            row       = 0
        )
        prev_btn.callback = self._on_previous
        self.add_item(prev_btn)

        self._play_pause_btn          = discord.ui.Button(
            emoji     = "⏸️",
            style     = discord.ButtonStyle.secondary,
            custom_id = "now_playing_play_pause",
            row       = 0
        )
        self._play_pause_btn.callback = self._on_play_pause
        self.add_item(self._play_pause_btn)

        next_btn          = discord.ui.Button(
            emoji     = "⏩",
            style     = discord.ButtonStyle.secondary,
            custom_id = "now_playing_next",
            row       = 0
        )
        next_btn.callback = self._on_next
        self.add_item(next_btn)

    ###########################################################################################################################
    ###########################################################################################################################

    async def _on_previous(self, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        previous_song = await self._music_manager.pop_last_played_song()
        if not previous_song:
            return

        await self._music_manager.prepare_back_playback(previous_song, self._music_manager.current_song)
        self._voice_client.stop()

    ###########################################################################################################################
    ###########################################################################################################################

    async def _on_play_pause(self, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        vc = self._voice_client
        if vc.is_paused():
            vc.resume()
            self._play_pause_btn.emoji = "⏸️"
        elif vc.is_playing():
            vc.pause()
            self._play_pause_btn.emoji = "▶️"

        # Update the button immediately; the updater will also sync on the next tick
        try:
            await interaction.message.edit(view = self)
        except Exception:
            pass

    ###########################################################################################################################
    ###########################################################################################################################

    async def _on_next(self, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        vc = self._voice_client
        if vc.is_playing() or vc.is_paused():
            vc.stop()

    ###########################################################################################################################
    ###########################################################################################################################

    def sync_play_pause(self, is_paused: bool) -> None:

        """
        Sync the play/pause button emoji to the current voice client pause state.

        Args:
            is_paused (bool): Whether the voice client is currently paused.

        Returns:
            None
        """

        self._play_pause_btn.emoji = "▶️" if is_paused else "⏸️"

###########################################################################################################################
###########################################################################################################################

def _format_time(seconds: float) -> str:

    """
    Convert a number of seconds into a human-readable time string.

    Args:
        seconds (float): Duration in seconds.

    Returns:
        str: Time formatted as "M:SS" or "H:MM:SS".
    """

    s    = int(seconds)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)

    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

###########################################################################################################################
###########################################################################################################################

def build_progress_bar(elapsed: float, duration: float, width: int = _PROGRESS_BAR_WIDTH, is_paused: bool = False) -> str:

    """
    Build a Unicode progress bar string for the Now Playing embed description.

    Args:
        elapsed (float): Seconds elapsed so far.
        duration (float): Total song duration in seconds.
        width (int): Number of bar characters.
        is_paused (bool): When True, shows ⏸ instead of ▶.

    Returns:
        str: Formatted progress bar, e.g. "▶⠀████████░░░░░░░░░░░░⠀3:45".
    """

    ratio  = max(0.0, min(elapsed / duration, 1.0))
    filled = int(ratio * width)
    bar    = "█" * filled + "░" * (width - filled)
    icon   = "❚❚" if is_paused else "▶"

    return f"{icon}⠀{bar}⠀{_format_time(elapsed)} / {_format_time(duration)}"

###########################################################################################################################
###########################################################################################################################

async def _send_now_playing_message(
    context     : commands.Context,
    song        : Song_Item,
    seek_offset : int = 0,
    lyric_line  : str = "",
    view        : Optional[discord.ui.View] = None
) -> discord.Message:

    """
    Build and send the initial Now Playing embed for a song that is about to start. When seek_offset is non-zero the
    progress bar is initialised at that position so there is no visual jump between the embed and the first updater tick.

    Args:
        context (commands.Context): Discord command context used to send the message.
        song (Song_Item): Song item that is about to play.
        seek_offset (int): Seconds into the song where playback starts (default 0).
        lyric_line (str): Initial lyric line shown below the progress bar (default "").
        view (Optional[discord.ui.View]): Button view to attach to the message (default None).

    Returns:
        discord.Message: The sent Discord message, used by Now_Playing_Updater to edit it later.
    """

    duration    = float(song.get("duration") or 0)
    initial_bar = build_progress_bar(float(seek_offset), duration) if duration else ""

    embed, embed_file = build_now_playing_embed(song, progress_bar = initial_bar, lyric_line = lyric_line)

    kwargs : dict = {"embed": embed}
    if embed_file:
        kwargs["file"] = embed_file
    if view is not None:
        kwargs["view"] = view

    return await context.send(**kwargs)

###########################################################################################################################
###########################################################################################################################

class Now_Playing_Updater:

    """
    Periodically edits a Now Playing embed to show song progress while a song is playing. Pause-aware: time does not
    advance while the voice client is paused.
    """

    def __init__(
        self,
        message      : discord.Message,
        song         : Song_Item,
        voice_client : discord.VoiceClient,
        start_time   : Optional[float] = None,
        seek_offset  : int = 0,
        lyrics_task  : Optional[asyncio.Task] = None,
        view         : Optional[discord.ui.View] = None
    ) -> None:

        """
        Initialise the updater. Does not start the background task; call start() to begin.

        Args:
            message (discord.Message): The Now Playing embed message to edit on each tick.
            song (Song_Item): The song currently playing, used for duration and embed content.
            voice_client (discord.VoiceClient): Active voice connection; checked each tick for pause state.
            start_time (Optional[float]): Event-loop timestamp when playback began. Resolved on the first _update_loop tick
                when None.
            seek_offset (int): Seconds into the song where playback starts; added to elapsed so the progress bar
                initialises at the correct position (default 0).
            lyrics_task (Optional[asyncio.Task]): Background task resolving to (lyrics, sync_offset). When None,
                lyrics are considered unavailable immediately.
            view (Optional[discord.ui.View]): Button view attached to the message; kept in sync with pause state
                on each tick.

        Returns:
            None
        """

        self._message      = message
        self._song         = song
        self._voice_client = voice_client
        self._start_time   = start_time
        self._seek_offset  = seek_offset
        self._lyrics_task  = lyrics_task
        self._lyrics       : Optional[List[Tuple[float, str]]] = None
        self._sync_offset  : float                             = 0.0
        self._lyrics_ready : bool                              = lyrics_task is None
        self._view         : Optional[discord.ui.View]         = view
        self._task         : Optional[asyncio.Task]            = None
        # Resolved play start time and accumulated pause duration — written by _update_loop,
        # read by external callers (e.g. the !rewind command) to compute accurate elapsed time
        self._play_start_time : float = start_time if start_time is not None else 0.0
        self._paused_acc      : float = 0.0

    #######################################################################################################################
    #######################################################################################################################

    async def start(self) -> None:

        """
        Spawn the background update task.

        Returns:
            None
        """

        self._task = asyncio.create_task(self._update_loop())

    #######################################################################################################################
    #######################################################################################################################

    async def stop(self) -> None:

        """
        Cancel the background update task and wait for it to finish cleanly. Safe to call before start().

        Returns:
            None
        """

        if self._lyrics_task is not None and not self._lyrics_task.done():
            self._lyrics_task.cancel()

        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    #######################################################################################################################
    #######################################################################################################################

    async def _update_loop(self) -> None:

        """
        Periodically edit the Now Playing embed until the task is cancelled or the message is gone. Exits immediately when
        duration is unknown. Accumulates time spent paused in _paused_acc so elapsed stays accurate across pause/resume
        cycles.

        Returns:
            None
        """

        duration = float(self._song.get("duration") or 0)
        if not duration:
            # No known duration: skip all updates rather than show a meaningless bar
            return

        loop = asyncio.get_running_loop()
        # Use the caller-supplied start time so elapsed matches actual playback, not task scheduling delay
        start_time            = self._start_time if self._start_time is not None else loop.time()
        self._play_start_time = start_time
        last_tick             = start_time

        while True:
            await asyncio.sleep(_UPDATE_INTERVAL)

            now = loop.time()

            # Accumulate time spent paused so elapsed stays accurate across pause/resume
            if self._voice_client.is_paused():
                self._paused_acc += now - last_tick
            last_tick = now

            elapsed      = max(0.0, min(now - start_time - self._paused_acc + self._seek_offset, duration))
            progress_bar = build_progress_bar(elapsed, duration, is_paused = self._voice_client.is_paused())

            if self._lyrics_task is not None and self._lyrics_task.done():
                self._lyrics, self._sync_offset = self._lyrics_task.result()
                self._lyrics_task  = None
                self._lyrics_ready = True

            if not self._lyrics_ready:
                lyric_line = MSG.LYRICS_RETRIEVING
            elif self._lyrics is None:
                lyric_line = MSG.LYRICS_NOT_FOUND
            else:
                lyric_line = get_current_lyric_line(self._lyrics, elapsed - self._sync_offset) or MSG.LYRICS_MUSIC

            embed, _     = build_now_playing_embed(self._song, progress_bar = progress_bar, lyric_line = lyric_line)

            # Sync play/pause button emoji with current voice state
            if self._view is not None:
                self._view.sync_play_pause(self._voice_client.is_paused())

            try:
                if self._view is not None:
                    await self._message.edit(embed = embed, view = self._view)
                else:
                    await self._message.edit(embed = embed)
            except Exception:
                # Message deleted or missing permissions: stop updating silently
                break

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
