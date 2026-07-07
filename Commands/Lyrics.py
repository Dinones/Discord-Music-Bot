###########################################################################################################################
#   Implements the !lyrics command, which shows the current lyric line and surrounding context as a Discord embed.        #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
import discord
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Music_Manager import get_music_manager

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_EMBED_COLOR = discord.Color.from_rgb(195, 0, 0)
_WINDOW_SIZE = 3

###########################################################################################################################
###########################################################################################################################

def _format_timestamp(seconds: float) -> str:

    """
    Format a float number of seconds as a bracketed M:SS timestamp string.

    Args:
        seconds (float): Playback position in seconds.

    Returns:
        str: Formatted timestamp, e.g. "[1:30]".
    """

    s = int(seconds)
    return f"[{s // 60}:{s % 60:02d}]"

###########################################################################################################################
###########################################################################################################################

async def lyrics(context: commands.Context) -> None:

    """
    Display the active lyric line and the _WINDOW_SIZE lines before and after it as a Discord embed. Sends an error
    message when the bot is not playing, lyrics are still being fetched, or no synced lyrics are available.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    music_manager = get_music_manager()
    song          = music_manager.current_song

    if not song:
        await context.send(MSG.BOT_NOT_PLAYING_ANYTHING)
        return

    updater = music_manager.current_updater

    if not updater:
        await context.send(MSG.BOT_NOT_PLAYING_ANYTHING)
        return

    if not updater._lyrics_ready:
        await context.send(MSG.LYRICS_RETRIEVING)
        return

    if not updater._lyrics:
        await context.send(MSG.LYRICS_NOT_FOUND)
        return

    # Compute current playback position and adjust for LRC sync offset
    loop     = asyncio.get_running_loop()
    elapsed  = max(0.0, loop.time() - updater._play_start_time - updater._paused_acc + updater._seek_offset)
    adjusted = elapsed - updater._sync_offset

    # Find the index of the active lyric line (last line whose timestamp does not exceed adjusted)
    lyrics_list = updater._lyrics
    current_idx = 0
    for i, (ts, _) in enumerate(lyrics_list):
        if ts <= adjusted:
            current_idx = i
        else:
            break

    start = max(0, current_idx - _WINDOW_SIZE)
    end   = min(len(lyrics_list), current_idx + _WINDOW_SIZE + 1)

    lines = []
    for i in range(start, end):
        ts, text = lyrics_list[i]
        label    = text or MSG.LYRICS_MUSIC
        ts_str   = _format_timestamp(ts)

        if i == current_idx:
            lines.append(f"**▶⠀{ts_str}⠀{label}**")
        else:
            lines.append(f"**{ts_str}**⠀{label}")

    title = song.get("title", "Unknown")
    url   = str(song.get("playback_query", "") or song.get("spotify_url", "")).strip()

    embed       = discord.Embed(title = title, description = "\n".join(lines), color = _EMBED_COLOR)
    embed.url   = url

    await context.send(embed = embed)

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "show lyrics",
            result = title
        )
    )

###########################################################################################################################
###########################################################################################################################

def register_lyrics_command(bot: commands.Bot) -> None:

    """
    Register the "!lyrics" command on the bot.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.

    Returns:
        None
    """

    @bot.command(name = "lyrics", aliases = ["ly"])
    async def lyrics_command(context: commands.Context) -> None:

        """
        Show the active lyric line and surrounding context for the currently playing song.
        """

        await lyrics(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
