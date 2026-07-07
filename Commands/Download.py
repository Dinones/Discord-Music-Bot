###########################################################################################################################
#   Implements the !download command, which downloads a YouTube song as an MP3 and sends it to the channel.              #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import tempfile
import discord
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Music_Manager import get_music_manager
from Utils.Reactions import send_reaction, remove_reaction
from Utils.Spotify import is_spotify_url
from Utils.Youtube import download_mp3

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = "Download"

###########################################################################################################################
###########################################################################################################################

async def download(context: commands.Context, args: str) -> None:

    """
    Download a YouTube song as an MP3, send it to the channel, then delete the local file.

    Args:
        context (commands.Context): Discord command context.
        args (str): YouTube URL or text search query.

    Returns:
        None
    """

    args = args.strip()

    if not args:
        await send_reaction(context.message, "❌")
        await context.send(MSG.DOWNLOAD_MISSING_ARGUMENT)
        return

    if is_spotify_url(args):
        await send_reaction(context.message, "❌")
        await context.send(MSG.DOWNLOAD_SPOTIFY_NOT_SUPPORTED)
        return

    await send_reaction(context.message, "⏳")

    music_manager = get_music_manager()

    with tempfile.TemporaryDirectory() as tmpdir:

        async with context.typing():
            result = await download_mp3(music_manager, context.message, args, tmpdir)

        if not result:
            await send_reaction(context.message, "❌")
            await remove_reaction(context.message, "⏳", context.bot.user)
            await context.send(MSG.DOWNLOAD_FAILED)
            return

        mp3_files = [f for f in os.listdir(tmpdir) if f.lower().endswith(".mp3")]

        if not mp3_files:
            await send_reaction(context.message, "❌")
            await remove_reaction(context.message, "⏳", context.bot.user)
            await context.send(MSG.DOWNLOAD_FAILED)
            return

        file_path   = os.path.join(tmpdir, mp3_files[0])
        file_size   = os.path.getsize(file_path)
        guild_limit = context.guild.filesize_limit if context.guild else 8 * 1024 * 1024

        if file_size > guild_limit:
            size_mb  = round(file_size / (1024 * 1024), 1)
            limit_mb = round(guild_limit / (1024 * 1024))
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = "send downloaded song",
                    reason = f"File too large ({size_mb} MB, limit {limit_mb} MB)"
                )
            )
            await send_reaction(context.message, "❌")
            await remove_reaction(context.message, "⏳", context.bot.user)
            await context.send(MSG.DOWNLOAD_FILE_TOO_LARGE.format(size = size_mb, limit = limit_mb))
            return

        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "download song",
                result = mp3_files[0]
            )
        )

        await context.send(file = discord.File(file_path))

    await send_reaction(context.message, "✅")
    await remove_reaction(context.message, "⏳", context.bot.user)

###########################################################################################################################
###########################################################################################################################

def register_download_command(bot: commands.Bot) -> None:

    """
    Register the "!download" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.

    Returns:
        None
    """

    @bot.command(name = "download", aliases = ["dl"])
    async def download_command(context: commands.Context, *, args: str = "") -> None:

        """
        Download a YouTube song as MP3 and send it to the channel.
        """

        await download(context, args)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
