###########################################################################################################################
#   Implements the !volume command, which adjusts the playback volume.                                                   #
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

def register_volume_command(bot: commands.Bot) -> None:

    """
    Register the "!volume" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "volume", aliases = ["vol"])
    async def volume(context: commands.Context, *, args: str = "") -> None:

        """
        Read or adjust the current playback volume. Scale is 0-100, where 50 is the default.
        """

        is_ready = await connect_to_voice_channel(context)

        if not is_ready:
            return

        args = args.strip()

        # Validate argument before touching the voice client
        if args and (not args.isdigit() or int(args) not in range(101)):
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'change the volume',
                    reason = f'Invalid volume "{args}"'
                )
            )
            await send_reaction(context.message, "❌")
            await context.send(MSG.VOLUME_INVALID_ARGUMENT)
            return

        voice_client = context.voice_client
        is_active    = voice_client.is_playing() or voice_client.is_paused()

        if not is_active:
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'change the volume',
                    reason = 'No music is being played'
                )
            )
            await send_reaction(context.message, "❌")
            await context.send(MSG.BOT_NOT_PLAYING_ANYTHING)
            return

        if not args:
            # Read and report the current volume (PCMVolumeTransformer range 0.0-2.0 → user range 0-100)
            current_volume = int(voice_client.source.volume * 50)
            print(
                STR.G_ACTION_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'request the volume',
                    result = f'Volume is at {current_volume}%'
                )
            )
            await send_reaction(context.message, "✅")
            await context.send(MSG.VOLUME_CURRENT_VOLUME.format(volume = current_volume))
            return

        # Map user value 0-100 to PCMVolumeTransformer range 0.0-2.0
        new_volume = int(args) * 2 / 100
        voice_client.source.volume = new_volume

        display_volume = int(args)
        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = 'change the volume',
                result = f'Volume changed to {display_volume}%'
            )
        )
        await send_reaction(context.message, "✅")

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
