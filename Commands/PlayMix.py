###########################################################################################################################
#   Implements the !playmix command, which queues a Spotify playlist or album in shuffle order.                          #
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

def register_playmix_command(bot: commands.Bot) -> None:

    """
    Register the "!playmix" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "playmix")
    async def playmix_command(context: commands.Context, *, args: str = "") -> None:

        """
        Queue songs, shuffle the queue, then start playback.
        """

        await play(context, args, shuffle = True)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
