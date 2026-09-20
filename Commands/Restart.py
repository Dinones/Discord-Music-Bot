###########################################################################################################################
#   Implements the !restart command, which restarts the bot after skull-reaction confirmation.                            #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
import subprocess
import discord
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Reactions import send_reaction

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME  = "Restart"
_SKULL       = "💀"
_TIMEOUT     = 30.0

###########################################################################################################################
###########################################################################################################################

async def restart(context: commands.Context) -> None:

    """
    Send a confirmation message with a 💀 reaction and wait for any user to react with 💀.
    Restarts the bot on confirmation, or cancels after 30 seconds with no response.
    Uses os.execv to replace the current process image so no external wrapper is needed.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    confirm_msg = await context.send(MSG.BOT_RESTART_CONFIRM)
    await send_reaction(confirm_msg, _SKULL)

    def _is_confirmation(reaction: discord.Reaction, user: discord.User) -> bool:
        return (
            str(reaction.emoji)       == _SKULL         and
            reaction.message.id       == confirm_msg.id and
            not user.bot
        )

    try:
        await context.bot.wait_for("reaction_add", check = _is_confirmation, timeout = _TIMEOUT)
    except asyncio.TimeoutError:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = context.author.name.capitalize(),
                action = "restart bot",
                reason = "Confirmation timed out"
            )
        )
        await context.send(MSG.BOT_RESTART_CANCELLED)
        return

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "restart bot",
            result = "Confirmed — closing connection and relaunching"
        )
    )

    await context.send(MSG.BOT_RESTARTING)

    # Close the WebSocket connection cleanly before launching the new process
    await context.bot.close()

    # subprocess.Popen quotes arguments with spaces correctly on Windows (os.execv does not)
    subprocess.Popen([sys.executable] + sys.argv)
    os._exit(0)

###########################################################################################################################
###########################################################################################################################

def register_restart_command(bot: commands.Bot) -> None:

    """
    Register the "!restart" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.

    Returns:
        None
    """

    @bot.command(name = "restart")
    async def restart_command(context: commands.Context) -> None:

        """
        Gracefully restart the bot.
        """

        await restart(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
