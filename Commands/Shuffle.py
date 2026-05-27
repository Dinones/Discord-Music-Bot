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
from Utils.Music_Manager import get_music_manager
from Commands.Connect import connect as connect_to_voice_channel

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def shuffle(context: commands.Context, send_feedback: bool = True) -> int:

    """
    Shuffle songs in the normal queue only.

    Args:
        context (commands.Context): Discord command context.
        send_feedback (bool): Whether to send Discord feedback messages.

    Returns:
        int: Number of songs in the normal queue after the shuffle attempt.
    """

    is_ready = await connect_to_voice_channel(context)

    if not is_ready:
        return 0

    music_manager = get_music_manager()
    shuffled_songs = await music_manager.shuffle_normal_queue()

    if send_feedback:
        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "shuffle songs in the normal queue",
                result = f"Shuffled {shuffled_songs} songs"
            )
        )

        await send_reaction(context.message, "✅")

    return shuffled_songs

###########################################################################################################################
###########################################################################################################################

def register_shuffle_command(bot: commands.Bot) -> None:

    """
    Register the "!shuffle" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "shuffle", aliases = ["mix"])
    async def shuffle_command(context: commands.Context) -> None:

        """
        Command wrapper that routes to the shared shuffle() helper.
        """

        await shuffle(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass


