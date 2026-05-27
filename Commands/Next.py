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

from Commands.Connect import connect as connect_to_voice_channel

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def skip(context: commands.Context) -> None:

    """
    Skip the currently playing or paused song.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    is_ready = await connect_to_voice_channel(context)

    if not is_ready:
        return

    voice_client = context.guild.voice_client if context.guild else None

    if not (voice_client and (voice_client.is_playing() or voice_client.is_paused())):
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = "skip song",
                reason = "Bot is not playing anything"
            )
        )
        await send_reaction(context.message, "❌")
        await context.send(MSG.BOT_NOT_PLAYING_ANYTHING)
        return

    voice_client.stop()

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "skip song",
            result = "Skipped current song"
        )
    )

    await send_reaction(context.message, "✅")

###########################################################################################################################
###########################################################################################################################

def register_next_command(bot: commands.Bot) -> None:

    """
    Register the "!next" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "next", aliases = ["skip", "n"])
    async def next_command(context: commands.Context) -> None:

        """
        Skip the currently playing song.
        """

        await skip(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
