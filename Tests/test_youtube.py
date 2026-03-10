###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

import os
import sys
import asyncio
import unittest
from unittest.mock import AsyncMock
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Utils.Youtube
import Utils.Constants as CONST
from Utils.Music_Manager import Music_Manager

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class TestSearchYoutubeVideo(unittest.IsolatedAsyncioTestCase):
    async def test_find_song_by_youtube_url(self) -> None:

        _Music_Manager = Music_Manager()
        message = AsyncMock(
            channel = AsyncMock(send = AsyncMock()),
            author  = AsyncMock(name = CONST.TESTING_AUTHOR_NAME)
        )

        result = await Utils.Youtube.search_youtube_video(_Music_Manager, message, CONST.TESTING_YOUTUBE_LINK)

        self.assertGreater(len(result.keys()), 0)

    #######################################################################################################################
    #######################################################################################################################

    async def test_find_song_by_youtube_search(self) -> None:

        _Music_Manager = Music_Manager()
        message = AsyncMock(
            channel = AsyncMock(send = AsyncMock()),
            author  = AsyncMock(name = CONST.TESTING_AUTHOR_NAME)
        )

        result = await Utils.Youtube.search_youtube_video(_Music_Manager, message, CONST.TESTING_YOUTUBE_QUERY)

        self.assertGreater(len(result.keys()), 0)

    #######################################################################################################################
    #######################################################################################################################

    

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer=True)