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
from Utils.Music_Manager import get_music_manager
from Utils.Reactions import send_reaction

from Commands.Connect import connect as connect_to_voice_channel

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def clear(context: commands.Context, send_feedback: bool = True) -> None:

    """
    Stop current playback (if any) and clear all queue structures.

    Args:
        context (commands.Context): Discord command context.
        send_feedback (bool): Whether to send Discord feedback message.

    Returns:
        None
    """

    is_ready = await connect_to_voice_channel(context)

    if not is_ready:
        return

    voice_client = context.voice_client
    if voice_client is not None and voice_client.is_connected():
        # Stop current playback so queue processing can unwind immediately
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()

    music_manager = get_music_manager()
    await music_manager.clear_all_queues()

    if send_feedback:
        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "clear music queues",
                result = "Playback stopped and all queues were cleared"
            )
        )
        await send_reaction(context.message, "✅")

###########################################################################################################################
###########################################################################################################################

def register_clear_command(bot: commands.Bot) -> None:

    """
    Register the "!clear" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "clear", aliases = ["stop"])
    async def clear_command(context: commands.Context) -> None:

        """
        Command wrapper that routes to the shared clear() helper.
        """

        await clear(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
