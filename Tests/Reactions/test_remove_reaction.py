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
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils.Reactions import remove_reaction
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Remove_Reaction(unittest.IsolatedAsyncioTestCase):

    async def test_remove_reaction_returns_true_and_calls_remove_reaction_on_success(self) -> None:

        member  = Mock()
        message = Mock(remove_reaction = AsyncMock())

        result = await remove_reaction(message, "⏳", member)

        self.assertTrue(
            result,
            _color_error_message_in_red(
                'remove_reaction() should return True when the reaction is removed successfully.'
            )
        )
        message.remove_reaction.assert_called_once_with("⏳", member)

    #######################################################################################################################
    #######################################################################################################################

    async def test_remove_reaction_returns_false_and_logs_on_exception(self) -> None:

        member  = Mock()
        message = Mock(remove_reaction = AsyncMock(side_effect = Exception("Missing permissions")))

        with (
            patch("Utils.Reactions.print"),
            patch("Utils.Reactions.save_exception_to_txt") as mock_log
        ):
            result = await remove_reaction(message, "⏳", member)

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'remove_reaction() should return False when an exception is raised.'
            )
        )
        mock_log.assert_called_once()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
