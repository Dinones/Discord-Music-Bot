###########################################################################################################################
#   Implements the !filter command, which sends a panel of toggle buttons for per-genre song filtering.                  #
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
from Utils import Constants as CONST
from Utils.Music_Manager import get_music_manager

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Filter'

###########################################################################################################################
###########################################################################################################################

class _Filter_Button(discord.ui.Button):

    def __init__(self, genre: str) -> None:

        music_manager = get_music_manager()
        active        = genre in music_manager.active_filters

        super().__init__(
            label     = genre,
            style     = discord.ButtonStyle.danger if active else discord.ButtonStyle.success,
            custom_id = f"filter_toggle_{genre.lower()}"
        )

        self._genre = genre

    #######################################################################################################################
    #######################################################################################################################

    async def callback(self, interaction: discord.Interaction) -> None:

        music_manager = get_music_manager()

        if self._genre in music_manager.active_filters:
            music_manager.active_filters.discard(self._genre)
            self.style = discord.ButtonStyle.success
        else:
            music_manager.active_filters.add(self._genre)
            self.style = discord.ButtonStyle.danger

        print(
            STR.G_ACTION_DONE.format(
                user   = interaction.user.name.capitalize(),
                action = f"toggle '{self._genre}' filter",
                result = "active" if self._genre in music_manager.active_filters else "inactive"
            )
        )

        await interaction.response.edit_message(view = self.view)

###########################################################################################################################
###########################################################################################################################

class _Filter_View(discord.ui.View):

    def __init__(self) -> None:

        super().__init__(timeout = None)

        for genre in CONST.GENRE_FILTERS:
            self.add_item(_Filter_Button(genre))

###########################################################################################################################
###########################################################################################################################

async def filter(context: commands.Context) -> None:

    """
    Send the filter toggle panel to the Discord channel.

    Args:
        context (commands.Context): Discord command context.

    Returns:
        None
    """

    view = _Filter_View()
    await context.send(view = view)

###########################################################################################################################
###########################################################################################################################

def register_filter_command(bot: commands.Bot) -> None:

    """
    Register the "!filter" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "filter")
    async def filter_command(context: commands.Context) -> None:

        """
        Command wrapper that routes to the shared filter() helper.
        """

        await filter(context)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
