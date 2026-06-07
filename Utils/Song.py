###########################################################################################################################
#   Song item normalization and stream URL resolution from YouTube and Spotify metadata.                                  #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
from typing import TypedDict, Optional, Literal, Dict, Any

from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils.Youtube import search_youtube_video, get_video_from_spotify_song

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Song_Item(TypedDict, total = False):

    """
    Typed structure for normalized queue songs shared across command modules.
    """

    source_type      : Literal["Youtube", "Spotify"]
    title            : str
    duration         : int
    requested_by     : str

    # YouTube source fields
    playback_query   : str

    # Spotify source fields
    spotify_title    : str
    spotify_authors  : str
    spotify_url      : str

    # Playback control fields
    seek_offset      : int

###########################################################################################################################
###########################################################################################################################

def build_song_item_from_youtube(video: Dict[str, Any], requested_by: str) -> Optional[Song_Item]:

    """
    Build a normalized queue song object from a YouTube payload.

    Args:
        video (Dict[str, Any]): YouTube video payload.
        requested_by (str): User name who requested the song.

    Returns:
        Optional[Song_Item]: Normalized song dictionary, or None if mandatory fields are missing.
    """

    playback_query = str(video.get("webpage_url", "")).strip() or str(video.get("id", "")).strip()
    song_title = str(video.get("title", "")).strip()

    if not playback_query or not song_title:
        return None

    return {
        "source_type"    : "Youtube",
        "title"          : song_title,
        "playback_query" : playback_query,
        "duration"       : int(video.get("duration", 0) or 0),
        "requested_by"   : requested_by
    }

###########################################################################################################################
###########################################################################################################################

def build_song_item_from_spotify_track(spotify_song: Dict[str, Any], requested_by: str) -> Optional[Song_Item]:

    """
    Build a normalized queue song object from a Spotify track payload.

    Args:
        spotify_song (Dict[str, Any]): Spotify track payload.
        requested_by (str): User name who requested the song.

    Returns:
        Optional[Song_Item]: Normalized song dictionary, or None if mandatory fields are missing.
    """

    song_title = str(spotify_song.get("name", "")).strip()

    if not song_title:
        return None

    song_authors = ", ".join(
        str(artist.get("name", "")).strip()
            for artist in spotify_song.get("artists", [])
                if str(artist.get("name", "")).strip()
    )

    return {
        "source_type"     : "Spotify",
        "title"           : song_title,
        "spotify_title"   : song_title,
        "spotify_authors" : song_authors,
        "spotify_url"     : str(spotify_song.get("external_urls", {}).get("spotify", "")),
        "requested_by"    : requested_by
    }

###########################################################################################################################
###########################################################################################################################

def enrich_song_from_video(song: Song_Item, resolved_video: Dict[str, Any]) -> None:

    """
    Backfill the YouTube URL and duration into a song item from a resolved video payload.

    Mutates the song in-place; safe to call on both YouTube and Spotify source songs.

    Args:
        song (Song_Item): Queue song item to enrich.
        resolved_video (Dict[str, Any]): Resolved YouTube video payload.

    Returns:
        None
    """

    # Store the resolved YouTube URL so the embed always links to YouTube, not Spotify
    if not song.get("playback_query"):
        youtube_url = str(resolved_video.get("webpage_url", "") or resolved_video.get("id", "")).strip()
        if youtube_url:
            song["playback_query"] = youtube_url

    # Backfill duration from the YouTube payload for Spotify songs (which have none initially)
    if not song.get("duration"):
        resolved_duration = int(resolved_video.get("duration", 0) or 0)
        if resolved_duration:
            song["duration"] = resolved_duration

###########################################################################################################################
###########################################################################################################################

async def resolve_song_stream_url(context: commands.Context, song: Song_Item) -> Optional[Dict[str, Any]]:

    """
    Resolve the playable YouTube stream payload for a queued song. Spotify songs are matched to a YouTube video
    just-in-time. YouTube songs are re-resolved from their stored URL to refresh expiring stream links.

    Args:
        context (commands.Context): Discord command context (used for error reporting in YouTube helper).
        song (Song_Item): Queue song item to resolve.

    Returns:
        Optional[Dict[str, Any]]: Resolved YouTube video payload, or None if resolution fails.
    """

    # Lazy import breaks the circular dependency with Music_Manager (which imports Song_Item from this module)
    from Utils.Music_Manager import get_music_manager

    music_manager = get_music_manager()

    source_type = str(song.get("source_type", "")).strip().lower()

    if source_type == "spotify":
        spotify_title   = str(song.get("spotify_title", "")).strip()
        spotify_authors = str(song.get("spotify_authors", "")).strip()

        if not spotify_title:
            return None

        return await asyncio.to_thread(
            get_video_from_spotify_song,
            music_manager,
            spotify_title,
            spotify_authors
        )

    playback_query = str(song.get("playback_query", "")).strip()
    if not playback_query:
        return None

    return await search_youtube_video(music_manager, context.message, playback_query)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
