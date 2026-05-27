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

async def resume(context: commands.Context) -> None:

    """
    Resume paused voice playback.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    is_ready = await connect_to_voice_channel(context)

    if not is_ready:
        return

    if not context.voice_client.is_paused():
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = 'resume playback',
                reason = 'Playback is not paused'
            )
        )
        await send_reaction(context.message, "❌")
        await context.send(MSG.BOT_NOT_PAUSED)
        return

    context.voice_client.resume()
    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "resume playback",
            result = "Playback resumed"
        )
    )
    await send_reaction(context.message, "✅")

###########################################################################################################################
###########################################################################################################################

def register_resume_command(bot: commands.Bot) -> None:

    """
    Register the "!resume" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "resume", aliases = ["unpause"])
    async def resume_command(context: commands.Context) -> None:

        """
        Command wrapper that routes to the shared resume() helper.
        """

        await resume(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
