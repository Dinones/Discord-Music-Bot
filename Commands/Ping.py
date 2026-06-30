###########################################################################################################################
#   Implements the !ping and !pong commands, which reply with the opposite command name.                                  #
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

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = "Ping"

###########################################################################################################################
###########################################################################################################################

async def ping(context: commands.Context) -> None:

    """
    Reply with !pong and the bot's current WebSocket heartbeat latency.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    latency = int(context.bot.latency * 1000)

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "ping",
            result = f"pong, latency is {latency} ms"
        )
    )

    await send_reaction(context.message, "🏓")
    await context.send(MSG.PING.format(latency = latency))

###########################################################################################################################
###########################################################################################################################

async def pong(context: commands.Context) -> None:

    """
    Reply with !ping and the bot's current WebSocket heartbeat latency.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    latency = int(context.bot.latency * 1000)

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "pong",
            result = f"ping, latency is {latency} ms"
        )
    )

    await send_reaction(context.message, "🏓")
    await context.send(MSG.PONG.format(latency = latency))

###########################################################################################################################
###########################################################################################################################

def register_ping_command(bot: commands.Bot) -> None:

    """
    Register the "!ping" and "!pong" commands.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.

    Returns:
        None
    """

    @bot.command(name = "ping")
    async def ping_command(context: commands.Context) -> None:
        await ping(context)

    @bot.command(name = "pong")
    async def pong_command(context: commands.Context) -> None:
        await pong(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
