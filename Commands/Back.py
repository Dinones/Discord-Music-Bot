###########################################################################################################################
#   Implements the !back command, which replays the previously played song.                                               #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Reactions import send_reaction
from Utils.Music_Manager import get_music_manager

from Utils.Music_Manager import process_global_queue
from Commands.Connect import connect as connect_to_voice_channel

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def back(context: commands.Context) -> None:

    """
    Replay the most recently played song by reinserting it at the front of the priority queue.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    is_ready = await connect_to_voice_channel(context)

    if not is_ready:
        return

    music_manager = get_music_manager()
    previous_song = await music_manager.pop_last_played_song()

    if not previous_song:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = "go back to previous song",
                reason = "No previous song in history"
            )
        )
        await send_reaction(context.message, "❌")
        await context.send(MSG.BACK_NO_PREVIOUS_SONG)
        return

    # Detect active playback to decide how to re-trigger the queue after reinsertion
    voice_client = context.guild.voice_client if context.guild else None
    is_active    = bool(voice_client and (voice_client.is_playing() or voice_client.is_paused()))
    current_song = music_manager.current_song if is_active else None

    await music_manager.prepare_back_playback(previous_song, current_song)

    if is_active:
        # Stop current playback; the running queue worker will naturally pick up the reinserted song
        voice_client.stop()
    else:
        # No active playback: start a new queue worker to begin playing immediately
        should_start = await music_manager.reserve_processing()
        if should_start:
            context.bot.loop.create_task(process_global_queue(context))

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "go back to previous song",
            result = f'Replaying "{previous_song.get("title", "Unknown title")}"'
        )
    )

    await send_reaction(context.message, "✅")

###########################################################################################################################
###########################################################################################################################

def register_back_command(bot: commands.Bot) -> None:

    """
    Register the "!back" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "back", aliases = ["prev", "previous"])
    async def back_command(context: commands.Context) -> None:

        """
        Replay the previous song.
        """

        await back(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
