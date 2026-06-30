###########################################################################################################################
#   Implements the !help command, which sends a Discord embed listing all available bot commands.                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import discord
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_EMBED_COLOR = discord.Color.from_rgb(195, 0, 0)

_SECTIONS = [
    (
        "🎵  Playing Music",
        (
            "`!play <url | title>`        ⠀Queue a YouTube or Spotify song / playlist\n"
            "`!playmix <url | title>`     ⠀Queue songs and shuffle before playing\n"
            "`!playnext <url | title>`    ⠀Add to priority queue (plays after current song)\n"
            "`!playnow <url | title>`     ⠀Interrupt and play immediately\n"
            "`!play_reverse <url | title>`⠀Queue a playlist in reverse order\n"
            "`!playlists`                 ⠀Show the saved playlist panel\n⠀"
        ),
    ),
    (
        "📋  Queue",
        (
            "`!queue`   ⠀Show the current queue\n"
            "`!shuffle` ⠀Shuffle the queue\n"
            "`!clear`   ⠀Clear queue and stop playback\n"
            "`!next [n]`⠀Skip 1 or N songs\n"
            "`!back`    ⠀Play the previous song\n⠀"
        ),
    ),
    (
        "⏯️  Playback",
        (
            "`!pause`                 ⠀Pause playback\n"
            "`!resume`                ⠀Resume playback\n"
            "`!seek <MM:SS | seconds>`⠀Jump to a specific position\n"
            "`!rewind <seconds>`      ⠀Rewind by N seconds\n"
            "`!volume [0-100]`        ⠀View or set volume  (default: 50)\n⠀"
        ),
    ),
    (
        "🔧  Other",
        (
            "`!connect`   ⠀Connect to your voice channel\n"
            "`!disconnect`⠀Disconnect from voice channel\n"
            "`!filter`    ⠀Toggle genre filters\n"
            "`!ping`      ⠀Check bot latency"
        ),
    ),
]

###########################################################################################################################
###########################################################################################################################

def build_help_embed() -> discord.Embed:

    """
    Build the help embed listing all available bot commands grouped by category.

    Returns:
        discord.Embed: Formatted help embed.
    """

    embed = discord.Embed(title = "Bot Commands", color = _EMBED_COLOR)

    for section_name, section_body in _SECTIONS:
        embed.add_field(name = section_name, value = section_body, inline = False)

    return embed

###########################################################################################################################
###########################################################################################################################

async def help(context: commands.Context) -> None:

    """
    Send the help embed listing all available bot commands.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "show help",
            result = "Help embed sent"
        )
    )

    await context.send(embed = build_help_embed())

###########################################################################################################################
###########################################################################################################################

def register_help_command(bot: commands.Bot) -> None:

    """
    Register the "!help" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.

    Returns:
        None
    """

    @bot.command(name = "help")
    async def help_command(context: commands.Context) -> None:

        """
        Show all available bot commands.
        """

        await help(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
