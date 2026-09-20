###########################################################################################################################
#   Implements the !play_reverse command, which queues songs in reversed order (last track plays first).                  #
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

from Commands.Play import play

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def play_reverse(context: commands.Context, args: str) -> None:

    """
    Queue songs in reversed order and start playback.

    Args:
        context (commands.Context): Discord command context.
        args (str): Youtube URL, Spotify URL or text query.

    Returns:
        None
    """

    await play(context, args, reverse = True)

###########################################################################################################################
###########################################################################################################################

def register_play_reverse_command(bot: commands.Bot) -> None:

    """
    Register the "!play_reverse" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.

    Returns:
        None
    """

    @bot.command(name = "play_reverse", aliases=["playreverse", "play_rev", "playrev"])
    async def play_reverse_command(context: commands.Context, *, args: str = "") -> None:

        """
        Command wrapper that routes to the shared play_reverse() helper.
        """

        await play_reverse(context, args)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
