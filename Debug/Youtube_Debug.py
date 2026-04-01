###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
from time import time
from typing import TYPE_CHECKING
from unittest.mock import Mock, AsyncMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils.Youtube import *
from Utils.Music_Manager import Music_Manager

if TYPE_CHECKING:
    from discord import Message

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Youtube'

###########################################################################################################################
###########################################################################################################################

# 1. Download MP3 from Youtube link
def _download_mp3_from_link(option):
    print(
        '\n' + 
        STR.M_SELECTED_OPTION.format(
            module = MODULE_NAME,
            option = option,
            action = "Downloading MP3 from Youtube link",
            path   = f'"{CONST.TESTING_YOUTUBE_LINK}"'
        )
    )

    _Music_Manager = Music_Manager()
    message = _build_test_message()

    MP3_DOWNLOAD_OUTPUT_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", CONST.TESTING_MP3_DOWNLOAD_OUTPUT_PATH)
    )

    if not os.path.exists(MP3_DOWNLOAD_OUTPUT_PATH):
        return print(
            STR.G_INVALID_PATH_ERROR.format(
                module = MODULE_NAME,
                path   = MP3_DOWNLOAD_OUTPUT_PATH
            )
        )

    video_title = asyncio.run(
        download_mp3(_Music_Manager, message, CONST.TESTING_YOUTUBE_LINK, MP3_DOWNLOAD_OUTPUT_PATH)
    )

    if not video_title:
        return print(
            STR.G_ACTION_NOT_DONE.format(
                user   = message.author.name.capitalize(),
                action = "download an MP3 from Youtube",
                reason = "Download failed"
            )
        )

    output_video_path = os.path.join(MP3_DOWNLOAD_OUTPUT_PATH, video_title)

    print(STR.YT_AUDIO_DOWNLOADED.format(output_path = output_video_path))

###########################################################################################################################
###########################################################################################################################

# 2. Search Youtube link
# 3. Search Youtube query
def _search_youtube_video(option):
    if option == '2':
        search_video = CONST.TESTING_YOUTUBE_LINK
    elif option == '3':
        search_video = CONST.TESTING_YOUTUBE_QUERY

    print(
        '\n' + 
        STR.M_SELECTED_OPTION.format(
            module = MODULE_NAME,
            option = option,
            action = "Searching on Youtube",
            path   = f'"{search_video}"'
        )
    )

    _Music_Manager = Music_Manager()
    message = _build_test_message()

    start_time = time()
    result = asyncio.run(search_youtube_video(_Music_Manager, message, search_video))

    if not result:
        return print(
            STR.G_ACTION_NOT_DONE.format(
                user   = message.author.name.capitalize(),
                action = "search something on Youtube",
                reason = "No results found"
            )
        )

    print(
        STR.YT_VIDEO_FOUND.format(
            seconds = str(round(time() - start_time, 2)),
            title   = result.get('title', '')
        )
    )

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

def main_menu():
        print('\n' + STR.M_MENU.format(module = MODULE_NAME))
        print(STR.M_MENU_OPTION.format(index = 1, option = 'Download MP3 from Youtube link'))
        print(STR.M_MENU_OPTION.format(index = 2, option = 'Search Youtube link'))
        print(STR.M_MENU_OPTION.format(index = 3, option = 'Search Youtube query'))

        option = input('\n' + STR.M_OPTION_SELECTION.format(module = MODULE_NAME))

        menu_options = {
            '1': _download_mp3_from_link,
            '2': _search_youtube_video,
            '3': _search_youtube_video,
        }

        if option in menu_options:
            menu_options[option](option)
        else:
            print('\n' + STR.M_INVALID_OPTION.format(module = MODULE_NAME) + '\n')

###########################################################################################################################
###########################################################################################################################

if __name__ == "__main__":
    main_menu()
    print()
