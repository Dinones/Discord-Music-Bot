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
from typing import TYPE_CHECKING
from unittest.mock import Mock, AsyncMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Utils.Youtube
import Utils.Constants as CONST
from Utils.Music_Manager import Music_Manager

if TYPE_CHECKING:
    from discord import Message

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class TestSearchYoutubeVideo(unittest.IsolatedAsyncioTestCase):
    async def test_find_song_by_youtube_url(self) -> None:

        _Music_Manager = Music_Manager()
        message = _build_test_message()

        result = await Utils.Youtube.search_youtube_video(_Music_Manager, message, CONST.TESTING_YOUTUBE_LINK)

        self.assertIsNotNone(result)
        self.assertGreater(len(result.keys()), 0)

    #######################################################################################################################
    #######################################################################################################################

    async def test_find_song_by_youtube_search(self) -> None:

        _Music_Manager = Music_Manager()
        message = _build_test_message()

        result = await Utils.Youtube.search_youtube_video(_Music_Manager, message, CONST.TESTING_YOUTUBE_QUERY)

        self.assertIsNotNone(result)
        self.assertGreater(len(result.keys()), 0)

    #######################################################################################################################
    #######################################################################################################################



###########################################################################################################################
###########################################################################################################################

def _build_test_message() -> Message:
    
    message = Mock(
        author = Mock(),
        channel = Mock(
            send = AsyncMock()
        )
    )

    message.author.name = CONST.TESTING_AUTHOR_NAME
        
    return message

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer=True)
