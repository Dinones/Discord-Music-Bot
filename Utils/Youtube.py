###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

# For import types
from __future__ import annotations

import os
import sys
import discord
from copy import deepcopy
from yt_dlp import YoutubeDL
from typing import TYPE_CHECKING, Optional, Dict, Any
from discord import PCMVolumeTransformer, FFmpegPCMAudio

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from Utils import Messages as MSG
from Utils import Constants as CONST
from Utils import Colored_Strings as STR

# Import types
if TYPE_CHECKING:
    from Utils.Music_Manager import Music_Manager
    from discord import Message

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Youtube'

###########################################################################################################################
###########################################################################################################################

def configure_ytdl(Music_Manager: Music_Manager) -> None:

    """
    Configures the YouTube-DL (yt-dlp) options for the given Music_Manager instance.

    Args:
        Music_Manager (Music_Manager): The Music_Manager class to configure with ytdl options.

    Returns:
        None
    """

    Music_Manager.ytdl_options = {
        'format': 'bestaudio/best',             # Chooses best audio quality
        'default_search': 'auto',
        'skip_download': True,                  # Only gets information, doesn't download
        'noprogress': True,                     # Hides the download progress bar
        'noplaylist': True,                     # Ignores playlists from searches
        'writedescription': False,              # Doesn't retrieve the video description

        'quiet': True,                          # Doesn't print messages to the console
        'verbose': False,                       # Doesn't print messages to the console
        'no_warnings': True,                    # Only critical error messages will be shown

        'postprocessors': [{        
            'key': 'FFmpegExtractAudio',        # Uses FFmpeg to extract audio from the video
            'preferredcodec': 'mp3',
            'preferredquality': '320',          # Maximum bitrate for MP3 is typically 320 kbps
        }]
    }

    YOUTUBE_COOKIES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", CONST.YT_COOKIES_FILE_PATH))

    # Bypass bot detection and allow access to age-restricted videos
    if os.path.exists(YOUTUBE_COOKIES_PATH):
        Music_Manager.ytdl_options.update(
            {
                'cookiefile': YOUTUBE_COOKIES_PATH
            }
        )
    else:
        print(
            STR.YT_COOKIES_FILE_NOT_FOUND.format(
                path = YOUTUBE_COOKIES_PATH
            )
        )

###########################################################################################################################
###########################################################################################################################

async def search_youtube_video(Music_Manager: Music_Manager, message: Message, args: str) -> Dict[str, Any]:

    """
    Searches for a YouTube video based on the provided input and returns information about the shortest video found.

    Args:
        Music_Manager (Music_Manager): The Music_Manager instance that holds YouTube-DL configuration.
        message (Message): The Discord message object containing author and channel information.
        args (str): The search query or YouTube URL.

    Returns:
        Dict[str, Any]: Information about the shortest video found, or an empty dictionary if the search fails.
    """
    
    # If the input is a Youtube link, search it; if not, search the first 2 query results
    if args.startswith('https://www.youtube.com/'):
        ytdl_options = _get_ytdl_options(Music_Manager, default_search = 'auto')
    else:
        ytdl_options = _get_ytdl_options(Music_Manager, default_search = 'ytsearch2')
        print(ytdl_options)
        args += 'lyrics'

    # Extracts the info from Youtube
    with YoutubeDL(ytdl_options) as ytdl:
        try:
            response = ytdl.extract_info(args, download=False)
            # The search was successful, but could not find any result
            if not response.get('entries', {}) and not response.get('title', ''):
                return {}
        except:
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = message.author.name.capitalize(),
                    action = 'play something from Youtube',
                    reason = f'Invalid Youtube input "{args}"'
                )
            )
            # await message.channel.send(MSG.DC_INVALID_LINK.replace('{platform}', 'Youtube'))
            return {}

    if response.get('entries', {}):
        shortest_video = min(response.get('entries', {}), key=lambda video: video['duration'])
    else:
        shortest_video = response
    
    return shortest_video

###########################################################################################################################
###########################################################################################################################

def get_video_from_spotify_song(Music_Manager: Music_Manager, song_title: str, song_authors: str) -> Dict[str, Any]:

    """
    Searches for a YouTube video based on a Spotify song's title and authors and returns the information about the
    shortest video found.

    Args:
        Music_Manager (Music_Manager): The Music_Manager instance that holds YouTube-DL configuration.
        song_title (str): The title of the Spotify song.
        song_authors (str): The name(s) of the song's author(s).

    Returns:
        Dict[str, Any]: A dictionary containing video details if found, otherwise an empty dictionary.
    """

    # Fetches top-2 search results
    ytdl_options = _get_ytdl_options(Music_Manager, default_search='ytsearch2')
    # Modify the search query to include song authors and "lyrics" for better results
    song_title += f' {song_authors} lyrics'

    # Extracts the info from Youtube
    with YoutubeDL(ytdl_options) as ytdl:
        try: 
            response = ytdl.extract_info(song_title, download = False)
            # The search was successful, but could not find any result
            if not response.get('entries', {}) and not response.get('title', ''):
                return {}
        except:
            print(STR.YT_COULD_NOT_UPDATE_SPOTIFY_SONG.format(reason = f'Invalid Youtube input "{song_title}"'))
            return {}

    if response.get('entries', {}):
        shortest_video = min(response.get('entries', {}), key=lambda video: video['duration'])
    else:
        shortest_video = response
    
    return shortest_video

###########################################################################################################################
###########################################################################################################################

def get_audio_player(raw_audio_url: str) -> Optional[PCMVolumeTransformer]:

    """
    Creates an audio player using FFmpeg for the given raw audio URL.

    Args:
        raw_audio_url (str): The raw audio URL.

    Returns:
        Optional[PCMVolumeTransformer]: The created audio player if successful, otherwise None in case of an error.
    """

    try:
        # Create an FFmpeg-based audio player
        player = PCMVolumeTransformer(
            FFmpegPCMAudio(
                raw_audio_url,
                before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options        = "-vn"
            )
        )

        return player

    except Exception as error:
        print(
            STR.G_SONG_PLAYER_ERROR.format(
                module = MODULE_NAME,
                error  = error
            )
        )
        
        return None

###########################################################################################################################
###########################################################################################################################

async def download_mp3(Music_Manager: Music_Manager, message: Message, youtube_url: str, output_path: str) -> str:

    """
    Downloads an MP3 file from a given YouTube URL using the specified Music_Manager configuration.

    Args:
        Music_Manager (Music_Manager): The Music_Manager class instance containing yt-dl options.
        message (Message): The Discord message object containing author and channel information.
        youtube_url (str): The URL of the YouTube video to download.
        output_path (str): The output directory where the MP3 file will be saved.

    Returns:
        str: The name of the saved file.
    """

    ytdl_options = _get_ytdl_options(
        Music_Manager,
        skip_download = False,
        outtmpl       = os.path.join(output_path, '%(title)s.%(ext)s') # Output path
    )

    with YoutubeDL(ytdl_options) as ytdl:
        try:
            video_info = ytdl.extract_info(youtube_url, download = True)
        except Exception as error:
            video_info = {}
            print(
                STR.YT_INVALID_YOUTUBE_LINK.format(
                    user   = CONST.TESTING_AUTHOR_NAME,
                    reason = error
                )
            )

    return f"{video_info.get('title', '')}.mp3" if video_info else 'ERROR'

###########################################################################################################################
###########################################################################################################################

def _get_ytdl_options(Music_Manager: Music_Manager, **overrides: Any) -> Dict[str, Any]:

    """
    Build a per-call yt-dlp options dictionary to avoid mutating a shared state.

    Args:
        Music_Manager (Music_Manager): The Music_Manager instance containing base yt-dlp options.
        **overrides (Any): Options that will be ovewritten for this specific call.

    Returns:
        Dict[str, Any]: A copy of yt-dlp options for one operation.
    """

    options = deepcopy(Music_Manager.ytdl_options)
    options.update(overrides)

    return options

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    import Debug.Youtube_Debug

    Debug.Youtube_Debug.main_menu()
    print()