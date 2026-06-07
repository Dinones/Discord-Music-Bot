###########################################################################################################################
#   Implements the !next and !skip commands, which skip the currently playing song.                                      #
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
from Utils.Embed.Queue import _MAX_SONGS

from Commands.Connect import connect as connect_to_voice_channel

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def skip(context: commands.Context, count: str = "") -> None:

    """
    Skip the currently playing or paused song, optionally skipping multiple songs at once.

    Args:
        context (commands.Context): Discord command context.
        count    (str): Number of songs to skip. Defaults to 1. Capped at _MAX_SONGS.

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

    try:
        skip_count = max(1, int(count))
    except (ValueError, TypeError):
        skip_count = 1

    capped = skip_count > _MAX_SONGS
    skip_count = min(skip_count, _MAX_SONGS)

    if capped:
        await context.send(MSG.SKIP_COUNT_CAPPED.format(max = _MAX_SONGS))

    # Drop skip_count-1 upcoming songs; stopping the current song counts as the first skip
    if skip_count > 1:
        await get_music_manager().drop_songs(skip_count - 1)

    voice_client.stop()

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "skip song",
            result = f"Skipped {skip_count} song(s)"
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
    async def next_command(context: commands.Context, count: str = "") -> None:

        """
        Skip the currently playing song, or skip multiple songs at once with an optional count.
        """

        await skip(context, count)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
