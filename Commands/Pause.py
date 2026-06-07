###########################################################################################################################
#   Implements the !pause command, which pauses the currently playing song.                                              #
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

def register_pause_command(bot: commands.Bot) -> None:

    """
    Register the "!pause" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "pause")
    async def pause(context: commands.Context) -> None:

        """
        Pause current voice playback.
        """

        is_ready = await connect_to_voice_channel(context)

        if not is_ready:
            return

        if context.voice_client.is_paused():
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'pause playback',
                    reason = 'Playback is already paused'
                )
            )
            await send_reaction(context.message, "❌")
            await context.send(MSG.BOT_ALREADY_PAUSED)
            return

        if not context.voice_client.is_playing():
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'pause playback',
                    reason = 'Bot is not playing any song'
                )
            )
            await send_reaction(context.message, "❌")
            await context.send(MSG.BOT_NOT_PLAYING_ANYTHING)
            return

        context.voice_client.pause()
        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "pause playback",
                result = "Playback paused"
            )
        )
        await send_reaction(context.message, "✅")

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
