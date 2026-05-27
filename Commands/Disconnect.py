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
from Commands.Clear import clear as clear_queue

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

def register_disconnect_command(bot: commands.Bot) -> None:

    """
    Register the "!disconnect" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "disconnect", aliases = ["leave"])
    async def disconnect(context: commands.Context) -> None:

        """
        Disconnect the bot from the current voice channel.
        """

        # User is sending a DM to the bot
        if context.guild is None:
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'disconnect the bot from a voice channel',
                    reason = 'User is sending a DM to the bot'
                )
            )
            await send_reaction(context.message, "❌")
            await context.send(MSG.USER_SENDING_DM_TO_BOT)
            return

        # Bot is not connected to any voice channel
        if context.voice_client is None:
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'disconnect the bot from a voice channel',
                    reason = 'Bot is not connected to any voice channel'
                )
            )
            await send_reaction(context.message, "❌")
            await context.send(MSG.BOT_NOT_CONNECTED_TO_VC)
            return

        # User is not connected to any voice channel
        if context.author.voice is None or context.author.voice.channel is None:
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'disconnect the bot from a voice channel',
                    reason = 'User is not connected to any voice channel'
                )
            )
            await send_reaction(context.message, "❌")
            await context.send(MSG.USER_NOT_CONNECTED_TO_VC)
            return

        # User is not connected to the same bot voice channel
        if context.author.voice.channel != context.voice_client.channel:
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'disconnect the bot from a voice channel',
                    reason = 'User is not connected to the same voice channel as the bot'
                )
            )
            await send_reaction(context.message, "❌")
            await context.send(MSG.USER_NOT_CONNECTED_TO_BOT_VC)
            return

        # Reset all queue states before disconnecting the bot from voice.
        await clear_queue(context, send_feedback = False)

        await context.voice_client.disconnect()
        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "disconnect the bot from a voice channel",
                result = "Bot disconnected from the voice channel"
            )
        )
        await send_reaction(context.message, "✅")

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
