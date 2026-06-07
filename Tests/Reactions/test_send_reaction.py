###########################################################################################################################
#   Tests for send_reaction() in Utils/Reactions.                                                                        #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Reactions import send_reaction
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Send_Reaction(unittest.IsolatedAsyncioTestCase):

    async def test_send_reaction_returns_true_and_calls_add_reaction_on_success(self) -> None:

        message = Mock(add_reaction = AsyncMock())

        result = await send_reaction(message, "✅")

        self.assertTrue(
            result,
            _color_error_message_in_red(
                'send_reaction() should return True when the reaction is added successfully.'
            )
        )
        message.add_reaction.assert_called_once_with("✅")

    #######################################################################################################################
    #######################################################################################################################

    async def test_send_reaction_returns_false_and_logs_on_exception(self) -> None:

        message = Mock(add_reaction = AsyncMock(side_effect = Exception("Missing permissions")))

        with (
            patch("Utils.Reactions.print"),
            patch("Utils.Reactions.save_exception_to_txt") as mock_log
        ):
            result = await send_reaction(message, "✅")

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'send_reaction() should return False when an exception is raised.'
            )
        )
        mock_log.assert_called_once()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
