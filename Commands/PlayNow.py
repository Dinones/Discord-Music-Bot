###########################################################################################################################
#   Implements the !playnow command, which immediately plays a song by interrupting the current one.                     #
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

from Commands.Next import skip
from Commands.PlayNext import playnext

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def playnow(context: commands.Context, args: str) -> None:

    """
    Add a single song to the front of the priority queue and skip the current song so it plays immediately.
    Falls back to a shuffled normal enqueue for playlists without skipping.

    Args:
        context (commands.Context): Discord command context.
        args (str): Youtube URL, Spotify URL or text query. Empty string resumes paused playback.

    Returns:
        None
    """

    was_single_song = await playnext(context, args, priority_front = True)

    # Only skip when something is actively playing or paused; no song to interrupt if the queue was idle
    if was_single_song:
        voice_client = context.guild.voice_client if context.guild else None
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            await skip(context)

###########################################################################################################################
###########################################################################################################################

def register_playnow_command(bot: commands.Bot) -> None:

    """
    Register the "!playnow" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "playnow", aliases = ["instant"])
    async def playnow_command(context: commands.Context, *, args: str = "") -> None:

        """
        Add a single song to the front of the priority queue and play it immediately.
        """

        await playnow(context, args)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
