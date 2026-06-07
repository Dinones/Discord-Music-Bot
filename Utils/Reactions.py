###########################################################################################################################
#   Helpers for adding and removing emoji reactions on Discord messages.                                                  #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import discord

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Logs import save_exception_to_txt

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = "Reactions"

###########################################################################################################################
###########################################################################################################################

async def send_reaction(message: discord.Message, emoji: str) -> bool:

    """
    Try to send an emoji reaction to a Discord message.

    Args:
        message (discord.Message): Target message that will receive the reaction.
        emoji (str): Emoji string to react with.

    Returns:
        bool: True when reaction is added successfully, False otherwise.
    """

    try:
        await message.add_reaction(emoji)
        return True

    except Exception as error:
        safe_emoji = emoji.encode("unicode_escape").decode("ascii")
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = MODULE_NAME,
                action = f'add reaction "{safe_emoji}" to a Discord message',
                reason = error
            )
        )
        save_exception_to_txt(error = error, title = "Send_Reaction")
        return False

###########################################################################################################################
###########################################################################################################################

async def remove_reaction(message: discord.Message, emoji: str, member: discord.abc.User) -> bool:

    """
    Try to remove the bot's own emoji reaction from a Discord message.

    Args:
        message (discord.Message): Target message to remove the reaction from.
        emoji (str): Emoji string to remove.
        member (discord.abc.User): The user whose reaction should be removed (typically the bot).

    Returns:
        bool: True when reaction is removed successfully, False otherwise.
    """

    try:
        await message.remove_reaction(emoji, member)
        return True

    except Exception as error:
        safe_emoji = emoji.encode("unicode_escape").decode("ascii")
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = MODULE_NAME,
                action = f'remove reaction "{safe_emoji}" from a Discord message',
                reason = error
            )
        )
        save_exception_to_txt(error = error, title = "Remove_Reaction")
        return False

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
