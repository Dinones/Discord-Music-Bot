###########################################################################################################################
#   Interactive debug menu for testing Spotify API search and track resolution functions.                                 #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import json
import asyncio
from time import time

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils.Spotify import *
from Debug.Helpers.Mock_Message import build_test_message

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Spotify'

###########################################################################################################################
###########################################################################################################################

# 1. Search Spotify song
# 2. Search Spotify songs from playlist
# 3. Search Spotify songs from album
def _get_spotify_songs(option: str) -> None:

    match option:
        case '1':
            search_link  = CONST.TESTING_SPOTIFY_SONG_LINK
            extra_string = ''
        case '2':
            search_link  = CONST.TESTING_SPOTIFY_PLAYLIST_LINK
            extra_string = 's from playlist'
        case '3':
            search_link  = CONST.TESTING_SPOTIFY_ALBUM_LINK
            extra_string = 's from album'

    print(
        STR.M_SELECTED_OPTION.format(
            module = MODULE_NAME,
            option = option,
            action = f"Retrieving Spotify song{extra_string}",
            path   = f'"{search_link}"'
        )
    )

    message    = build_test_message()
    start_time = time()

    songs = asyncio.run(search_spotify_songs(message, search_link))

    if not songs:
        return print(
            STR.G_ACTION_NOT_DONE.format(
                user   = message.author.name.capitalize(),
                action = f"retrieve Spotify song{extra_string}",
                reason = "Unexpected error"
            )
        )

    print(
        STR.SP_SONGS_FOUND.format(
            number       = len(songs),
            seconds      = round(time() - start_time, 2),
            spotify_link = search_link
        )
    )

    response = input(STR.SP_ASK_TO_PRINT_FIRST_SONG).strip().lower()
    if response in ('', 'y', 'yes'):
        print('\n', json.dumps(songs[0], indent=4, ensure_ascii=False, default=str))

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

def main_menu():
        print('\n' + STR.M_MENU.format(module = MODULE_NAME))
        print(STR.M_MENU_OPTION.format(index = 1, option = 'Retrieve Spotify song'))
        print(STR.M_MENU_OPTION.format(index = 2, option = 'Retriene Spotify songs from playlist'))
        print(STR.M_MENU_OPTION.format(index = 3, option = 'Retrieve Spotify songs from album'))

        option = input('\n' + STR.M_OPTION_SELECTION.format(module = MODULE_NAME))

        menu_options = {
            '1': _get_spotify_songs,
            '2': _get_spotify_songs,
            '3': _get_spotify_songs,
        }

        if option in menu_options:
            print()
            menu_options[option](option)
            print()
        else:
            print('\n' + STR.M_INVALID_OPTION.format(module = MODULE_NAME) + '\n')

###########################################################################################################################
###########################################################################################################################

if __name__ == "__main__":
    main_menu()