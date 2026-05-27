###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from typing import Any, Callable
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Commands.PlayMix
import Utils.Constants as CONST
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class _Fake_Bot:

    def __init__(self) -> None:
        self.registered_commands = {}

    #######################################################################################################################
    #######################################################################################################################

    def command(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:

        def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
            command_name = kwargs.get("name", function.__name__)
            self.registered_commands[command_name] = function
            return function

        return decorator

###########################################################################################################################
###########################################################################################################################

class Test_Register_PlayMix_Command(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        self.bot = _Fake_Bot()
        Commands.PlayMix.register_playmix_command(self.bot)
        self.playmix_command = self.bot.registered_commands.get("playmix")

    #######################################################################################################################
    #######################################################################################################################

    async def test_register_playmix_command_registers_playmix_function(self) -> None:

        self.assertIsNotNone(
            self.playmix_command,
            _color_error_message_in_red(
                'The "register_playmix_command()" function should have registered the "playmix" command.'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    async def test_playmix_calls_play_with_shuffle_true(self) -> None:

        context = Mock(author = Mock())
        context.author.name = CONST.TESTING_AUTHOR_NAME

        with patch("Commands.PlayMix.play", new = AsyncMock()) as mock_play:
            await self.playmix_command(context, args = "some song")

        mock_play.assert_called_once_with(context, "some song", shuffle = True)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
