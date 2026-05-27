###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utils import Constants as CONST

if TYPE_CHECKING:
    from discord import Message

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

def build_test_message() -> Message:
    
    message = Mock(
        author  = Mock(),
        channel = Mock(
            send = AsyncMock()
        )
    )

    message.author.name = CONST.TESTING_AUTHOR_NAME
        
    return message