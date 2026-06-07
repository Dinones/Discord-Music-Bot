###########################################################################################################################
#   Implements the !playlists command, which sends a button panel for each configured Spotify playlist.                  #
#   Clicking a button clears the normal queue and starts a shuffled playback of the selected playlist.                  #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import discord
from typing import Any
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Commands.Clear import clear
from Commands.Play import play
from Utils.Playlists import get_playlists
from Utils import Colored_Strings as STR

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Playlists'

###########################################################################################################################
###########################################################################################################################

class _Interaction_Context:

    """Minimal duck-typed context built from a button interaction for use with clear() and play()."""

    def __init__(self, interaction: discord.Interaction, bot: commands.Bot) -> None:

        self.guild   = interaction.guild
        self.author  = interaction.user
        self.channel = interaction.channel
        self.message = interaction.message
        self.bot     = bot

    #######################################################################################################################
    #######################################################################################################################

    @property
    def voice_client(self) -> discord.VoiceClient | None:
        return self.guild.voice_client if self.guild else None

    #######################################################################################################################
    #######################################################################################################################

    async def send(self, *args: Any, **kwargs: Any) -> discord.Message | None:
        return await self.channel.send(*args, **kwargs)

###########################################################################################################################
###########################################################################################################################

class _Playlist_Button(discord.ui.Button):

    def __init__(self, name: str, url: str, bot: commands.Bot) -> None:

        super().__init__(
            label     = name,
            style     = discord.ButtonStyle.primary,
            custom_id = f"playlist_{name.lower().replace(' ', '_')}"
        )

        self._url = url
        self._bot = bot

    #######################################################################################################################
    #######################################################################################################################

    async def callback(self, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        await interaction.message.delete()

        print(
            STR.G_ACTION_DONE.format(
                user   = interaction.user.name.capitalize(),
                action = f"select playlist '{self.label}'",
                result = "clearing queue and starting shuffled playback"
            )
        )

        ctx = _Interaction_Context(interaction, self._bot)
        await clear(ctx, send_feedback = False)
        await play(ctx, self._url, shuffle = True)

###########################################################################################################################
###########################################################################################################################

class _Playlists_View(discord.ui.View):

    def __init__(self, bot: commands.Bot) -> None:

        super().__init__(timeout = None)

        for playlist in get_playlists():
            self.add_item(_Playlist_Button(
                name = playlist["name"],
                url  = playlist["url"],
                bot  = bot
            ))

###########################################################################################################################
###########################################################################################################################

async def playlists(context: commands.Context) -> None:

    """
    Send a button panel listing all configured Spotify playlists.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    if not get_playlists():
        await context.send(MSG.NO_PLAYLISTS_CONFIGURED)
        return

    view = _Playlists_View(context.bot)
    await context.send(view = view)

    print(
        STR.G_ACTION_DONE.format(
            user   = context.author.name.capitalize(),
            action = "open playlists panel",
            result = f"{len(get_playlists())} playlist(s) shown"
        )
    )

###########################################################################################################################
###########################################################################################################################

async def send_playlists_panel(channel: discord.abc.Messageable, bot: commands.Bot) -> None:

    """
    Send the playlists button panel directly to a channel without a command context. Used at bot startup.

    Args:
        channel (discord.abc.Messageable): Channel to send the panel to.
        bot (commands.Bot): Bot instance passed into buttons so they can build an interaction context on click.

    Returns:
        None
    """

    if not get_playlists():
        return

    view = _Playlists_View(bot)
    await channel.send(view = view)

    print(
        STR.G_ACTION_DONE.format(
            user   = MODULE_NAME,
            action = "send startup playlists panel",
            result = f"{len(get_playlists())} playlist(s) shown"
        )
    )

###########################################################################################################################
###########################################################################################################################

def register_playlists_command(bot: commands.Bot) -> None:

    """
    Register the "!playlists" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "playlists", aliases=["playlist"])
    async def playlists_command(context: commands.Context) -> None:

        """
        Command wrapper that routes to the shared playlists() helper.
        """

        await playlists(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
