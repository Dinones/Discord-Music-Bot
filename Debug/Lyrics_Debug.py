###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
from time import time
from typing import Optional, List, Tuple

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils.Lyrics import fetch_lyrics, get_current_lyric_line
import Utils.Constants as CONST
import Utils.Colored_Strings as STR

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Lyrics'

###########################################################################################################################
###########################################################################################################################

# 1. Fetch lyrics by title + artist + duration (Spotify-style lookup)
def _fetch_with_artist(option: str) -> None:

    title    = CONST.TESTING_LYRICS_TITLE
    artist   = CONST.TESTING_LYRICS_ARTIST
    duration = CONST.TESTING_LYRICS_DURATION

    print(
        STR.M_SELECTED_OPTION.format(
            module = MODULE_NAME,
            option = option,
            action = "Fetching lyrics",
            path   = f'"{title}" by {artist} ({duration}s)'
        )
    )

    start_time = time()
    lyrics     = fetch_lyrics(title = title, artists = artist, duration = duration)
    elapsed    = round(time() - start_time, 2)

    _print_result(lyrics, elapsed, title)

###########################################################################################################################
###########################################################################################################################

# 2. Fetch lyrics by title only (YouTube-style lookup, no artist)
def _fetch_without_artist(option: str) -> None:

    title = CONST.TESTING_LYRICS_TITLE

    print(
        STR.M_SELECTED_OPTION.format(
            module = MODULE_NAME,
            option = option,
            action = "Fetching lyrics (no artist)",
            path   = f'"{title}"'
        )
    )

    start_time = time()
    lyrics     = fetch_lyrics(title = title, artists = "", duration = 0)
    elapsed    = round(time() - start_time, 2)

    _print_result(lyrics, elapsed, title)

###########################################################################################################################
###########################################################################################################################

# 3. Fetch lyrics from a custom input
def _fetch_custom(option: str) -> None:

    print(
        STR.M_SELECTED_OPTION.format(
            module = MODULE_NAME,
            option = option,
            action = "Fetching lyrics from custom input",
            path   = ""
        )
    )

    title    = input("  Title:    ").strip()
    artist   = input("  Artist:   ").strip()
    duration = input("  Duration: ").strip()

    if not title:
        return print(
            STR.G_ACTION_NOT_DONE.format(
                user   = MODULE_NAME,
                action = "fetch lyrics",
                reason = "Title cannot be empty"
            )
        )

    duration_int = int(duration) if duration.isdigit() else 0

    start_time = time()
    lyrics     = fetch_lyrics(title = title, artists = artist, duration = duration_int)
    elapsed    = round(time() - start_time, 2)

    _print_result(lyrics, elapsed, title)

###########################################################################################################################
###########################################################################################################################

def _print_result(lyrics: Optional[List[Tuple[float, str]]], elapsed: float, title: str) -> None:

    """
    Display lyrics fetch results, including the first 5 lines and the active line at 60 seconds.

    Args:
        lyrics  (Optional[List[Tuple[float, str]]]): Parsed lyrics, or None if unavailable.
        elapsed (float): Time taken to fetch in seconds.
        title   (str):   Song title for display.

    Returns:
        None
    """

    if not lyrics:
        return print(
            STR.G_ACTION_NOT_DONE.format(
                user   = MODULE_NAME,
                action = f'fetch lyrics for "{title}"',
                reason = f"No synced lyrics found ({elapsed}s)"
            )
        )

    print(
        STR.G_ACTION_DONE.format(
            user   = MODULE_NAME,
            action = f'fetch lyrics for "{title}"',
            result = f"{len(lyrics)} lines in {elapsed}s"
        )
    )

    print("\n  First 5 lines:")
    for timestamp, text in lyrics[:5]:
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        print(f"    [{minutes:02d}:{seconds:02d}]  {text}")

    sample_position = 60.0
    line_at_60      = get_current_lyric_line(lyrics, sample_position)
    print(f"\n  Active line at {int(sample_position)}s:  {line_at_60!r}")

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

def main_menu() -> None:

    print('\n' + STR.M_MENU.format(module = MODULE_NAME))
    print(STR.M_MENU_OPTION.format(index = 1, option = f'Fetch lyrics: "{CONST.TESTING_LYRICS_TITLE}" by {CONST.TESTING_LYRICS_ARTIST} ({CONST.TESTING_LYRICS_DURATION}s)'))
    print(STR.M_MENU_OPTION.format(index = 2, option = f'Fetch lyrics: "{CONST.TESTING_LYRICS_TITLE}" - no artist, no duration'))
    print(STR.M_MENU_OPTION.format(index = 3, option = 'Fetch lyrics: custom input'))

    option = input('\n' + STR.M_OPTION_SELECTION.format(module = MODULE_NAME))

    menu_options = {
        '1': _fetch_with_artist,
        '2': _fetch_without_artist,
        '3': _fetch_custom,
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
