###########################################################################################################################
#   Implements the !seek command, which jumps to an exact position in the currently playing song.                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
from typing import Optional
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Music_Manager import get_music_manager
from Utils.Reactions import send_reaction
from Commands.Connect import connect as connect_to_voice_channel

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def seek(context: commands.Context, args: str) -> None:

    """
    Jump to an exact position in the currently playing or paused song. Re-queues a copy of the current song with the
    requested seek_offset, then stops current playback so the queue worker picks up the copy immediately.

    Args:
        context (commands.Context): Discord command context.
        args (str): Target position as MM:SS or plain seconds (e.g. "1:30" or "90").

    Returns:
        None
    """

    is_ready = await connect_to_voice_channel(context)
    if not is_ready:
        return

    args    = args.strip()
    seek_to = _parse_seek_arg(args)

    if seek_to is None:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = "seek song",
                reason = f'Invalid argument "{args}"'
            )
        )
        await send_reaction(context.message, "❌")
        await context.send(MSG.SEEK_INVALID_ARGUMENT)
        return

    voice_client = context.guild.voice_client if context.guild else None
    is_active    = bool(voice_client and (voice_client.is_playing() or voice_client.is_paused()))

    if not is_active:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = "seek song",
                reason = "No music is being played"
            )
        )
        await send_reaction(context.message, "❌")
        await context.send(MSG.BOT_NOT_PLAYING_ANYTHING)
        return

    music_manager = get_music_manager()
    current_song  = music_manager.current_song

    if not current_song:
        await send_reaction(context.message, "❌")
        await context.send(MSG.BOT_NOT_PLAYING_ANYTHING)
        return

    # Clamp to song duration so seeking past the end doesn't immediately skip the song
    duration = int(current_song.get("duration") or 0)
    if duration:
        seek_to = min(seek_to, duration)

    song_copy              = dict(current_song)
    song_copy["seek_offset"] = seek_to

    await music_manager.prepare_rewind_playback(song_copy)

    # Stopping fires _after_playing → song_finished_event → the queue worker advances and
    # picks up the seek copy from the priority queue
    voice_client.stop()

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "seek song",
            result = f"Seeking to {seek_to}s"
        )
    )
    await send_reaction(context.message, "✅")

###########################################################################################################################
###########################################################################################################################

def _parse_seek_arg(args: str) -> Optional[int]:

    """
    Parse a seek position from a string. Accepts MM:SS format or a plain non-negative integer.

    Args:
        args (str): Raw argument string.

    Returns:
        Optional[int]: Position in seconds, or None if the input is invalid.
    """

    if ":" in args:
        parts = args.split(":", 1)
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            return int(parts[0]) * 60 + int(parts[1])
        return None

    if args.isdigit():
        return int(args)

    return None

###########################################################################################################################
###########################################################################################################################

def register_seek_command(bot: commands.Bot) -> None:

    """
    Register the "!seek" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.

    Returns:
        None
    """

    @bot.command(name = "seek", aliases = ["sk"])
    async def seek_command(context: commands.Context, *, args: str = "") -> None:

        """
        Jump to an exact position in the current song. Accepts MM:SS or plain seconds.
        """

        await seek(context, args)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
