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
from typing import Optional
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Song import Song_Item
from Utils.Embed.Now_Playing import build_now_playing_embed

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

# Seconds between embed edits (~1 update per 5 s keeps well within Discord's rate limits)
_UPDATE_INTERVAL   = 1
_PROGRESS_BAR_WIDTH = 20

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
    seek_offset : int = 0
) -> discord.Message:

    """
    Build and send the initial Now Playing embed for a song that is about to start. When seek_offset is non-zero the
    progress bar is initialised at that position so there is no visual jump between the embed and the first updater tick.

    Args:
        context (commands.Context): Discord command context used to send the message.
        song (Song_Item): Song item that is about to play.
        seek_offset (int): Seconds into the song where playback starts (default 0).

    Returns:
        discord.Message: The sent Discord message, used by Now_Playing_Updater to edit it later.
    """

    duration    = float(song.get("duration") or 0)
    initial_bar = build_progress_bar(float(seek_offset), duration) if duration else ""

    embed, embed_file = build_now_playing_embed(song, progress_bar = initial_bar)

    if embed_file:
        return await context.send(embed = embed, file = embed_file)

    return await context.send(embed = embed)

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
        seek_offset  : int = 0
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

        Returns:
            None
        """

        self._message      = message
        self._song         = song
        self._voice_client = voice_client
        self._start_time   = start_time
        self._seek_offset  = seek_offset
        self._task         : Optional[asyncio.Task] = None
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
            embed, _     = build_now_playing_embed(self._song, progress_bar = progress_bar)

            try:
                await self._message.edit(embed = embed)
            except Exception:
                # Message deleted or missing permissions: stop updating silently
                break

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
