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
from Utils.Logs import save_exception_to_txt

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def connect(context: commands.Context) -> bool:

    """
    Ensure bot is connected to the caller voice channel.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        bool: True if bot is connected to the caller voice channel, False otherwise.
    """

    action = "connect the bot to a voice channel"

    # User is sending a DM to the bot
    if context.guild is None:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = action,
                reason = 'User is sending a DM to the bot'
            )
        )
        await send_reaction(context.message, '❌')
        await context.send(MSG.USER_SENDING_DM_TO_BOT)

        return False

    # User is not connected to any voice channel
    if context.author.voice is None or context.author.voice.channel is None:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = action,
                reason = 'User is not connected to any voice channel'
            )
        )
        await send_reaction(context.message, '❌')
        await context.send(MSG.USER_NOT_CONNECTED_TO_VC)

        return False

    try:
        voice_channel = context.author.voice.channel

        # Bot is connected to a voice channel
        if context.voice_client is not None:
            # Move to the new voice channel
            if context.voice_client.channel != voice_channel:
                await context.voice_client.move_to(voice_channel)

            return True

        # Connect to the voice channel
        await voice_channel.connect()

        return True

    except Exception as error:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = action,
                reason = error
            )
        )

        save_exception_to_txt(error = error, title = 'Connect')
        await send_reaction(context.message, '❌')
        await context.send(MSG.BOT_COULD_NOT_CONNECT_TO_VC)

        return False

###########################################################################################################################
###########################################################################################################################

def register_connect_command(bot: commands.Bot) -> None:

    """
    Register the "!connect" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "connect", aliases = ["join"])
    async def connect_command(context: commands.Context) -> None:

        """
        Command wrapper that routes to the shared connect() helper.
        """

        is_ready = await connect(context)
        if is_ready:
            await send_reaction(context.message, '✅')

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
