###########################################################################################################################
#                                                                                                                         #
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
from Utils.Embed.Queue import build_queue_embed
from Utils.Music_Manager import get_music_manager

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def queue(context: commands.Context) -> None:

    """
    Fetch the current queue snapshot and send it as a Discord embed.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    music_manager = get_music_manager()
    current_song, priority, normal = await music_manager.get_full_queue_snapshot()

    if not current_song and not priority and not normal:
        await context.send(MSG.BOT_NOT_PLAYING_ANYTHING)
        await send_reaction(context.message, "❌")
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = "check the queue",
                reason = "Queue is empty"
            )
        )
        return

    total = len(priority) + len(normal)
    await send_reaction(context.message, "✅")
    await context.send(embed = build_queue_embed(current_song, priority, normal))
    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "check the queue",
            result = f'{total} song{"s" if total != 1 else ""} in queue'
        )
    )

###########################################################################################################################
###########################################################################################################################

def register_queue_command(bot: commands.Bot) -> None:

    """
    Register the "!queue" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "queue", aliases = ["q", "list"])
    async def queue_command(context: commands.Context) -> None:

        """
        Show the current music queue as an embed.
        """

        await queue(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
