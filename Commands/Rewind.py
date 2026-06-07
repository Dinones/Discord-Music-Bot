###########################################################################################################################
#   Implements the !rewind command, which seeks backwards in the currently playing song.                                 #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
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

MODULE_NAME = "Rewind"

###########################################################################################################################
###########################################################################################################################

async def rewind(context: commands.Context, args: str) -> None:

    """
###########################################################################################################################
    Seek the current song backward by the given number of seconds. Re-queues a copy of the current song at the front of the
    priority queue with seek_offset, then stops the current playback so the queue worker picks up the copy immediately. If
    the requested rewind exceeds elapsed time the song restarts from the beginning.

    Args:
        context (commands.Context): Discord command context.
        args (str): Number of seconds to rewind, must be a positive integer.

    Returns:
        None
    """

    is_ready = await connect_to_voice_channel(context)
    if not is_ready:
        return

    args = args.strip()

    if not args.isdigit() or int(args) <= 0:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = "rewind song",
                reason = f'Invalid argument "{args}"'
            )
        )
        await send_reaction(context.message, "❌")
        await context.send(MSG.REWIND_INVALID_ARGUMENT)
        return

    voice_client = context.guild.voice_client if context.guild else None
    is_active    = bool(voice_client and (voice_client.is_playing() or voice_client.is_paused()))

    if not is_active:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = "rewind song",
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

    # Compute accurate elapsed time using the updater's pause-aware accumulators
    updater = music_manager.current_updater
    if updater is not None:
        now     = asyncio.get_running_loop().time()
        elapsed = max(0.0, now - updater._play_start_time - updater._paused_acc + updater._seek_offset)
    else:
        elapsed = 0.0

    rewind_seconds = int(args)
    seek_to        = max(0, int(elapsed) - rewind_seconds)

    # Copy the song so the original in played_queue is unaffected
    song_copy               = dict(current_song)
    song_copy["seek_offset"] = seek_to

    await music_manager.prepare_rewind_playback(song_copy)

    # Stopping fires _after_playing → song_finished_event → the queue worker advances and
    # picks up the rewind copy from the priority queue
    voice_client.stop()

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "rewind song",
            result = f"Rewinding {rewind_seconds}s (seek to {seek_to}s)"
        )
    )
    await send_reaction(context.message, "✅")

###########################################################################################################################
###########################################################################################################################

def register_rewind_command(bot: commands.Bot) -> None:

    """
    Register the "!rewind" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.

    Returns:
        None
    """

    @bot.command(name = "rewind", aliases = ["rw"])
    async def rewind_command(context: commands.Context, *, args: str = "") -> None:

        """
        Rewind the current song by the given number of seconds.
        """

        await rewind(context, args)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
