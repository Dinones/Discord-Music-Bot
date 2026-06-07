###########################################################################################################################
#   Builds the Now Playing Discord embed with song metadata, thumbnail, and progress bar.                                #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import discord
import datetime
from typing import Optional, Tuple

from Utils.Song import Song_Item
from Utils import Constants as CONST

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_EMBED_COLOR   = discord.Color.from_rgb(195, 0, 0)
_MAX_TITLE_LEN = 52

###########################################################################################################################
###########################################################################################################################

def build_now_playing_embed(song: Song_Item, progress_bar: str = "") -> Tuple[discord.Embed, Optional[discord.File]]:

    """
    Build a Discord embed for the currently playing song.

    Args:
        song (Song_Item): The song that just started playing.

    Returns:
        Tuple[discord.Embed, Optional[discord.File]]: The embed and an attached disc GIF file, or None if unavailable.
    """

    # Build title: append Spotify authors when present, strip "lyrics" noise, truncate to Discord embed limit
    title   = str(song.get("title",          "")).strip()
    authors = str(song.get("spotify_authors", "")).strip()

    formatted_title = f"{title} - {authors}".strip() if authors else title
    formatted_title = formatted_title.replace("lyrics", "").strip()

    if len(formatted_title) > _MAX_TITLE_LEN:
        formatted_title = f"{formatted_title[:_MAX_TITLE_LEN - 3]}..."

    # Prefer the resolved YouTube URL; fall back to Spotify URL for songs not yet processed
    url = str(song.get("playback_query", "") or song.get("spotify_url", "")).strip()

    # Embed title and URL
    embed = discord.Embed(title = formatted_title or "Unknown", color = _EMBED_COLOR)
    if url:
        embed.url = url
    if progress_bar:
        embed.description = progress_bar

    # Footer
    requested_by  = str(song.get("requested_by", "")).strip()
    footer_kwargs : dict = {"text": f"By {requested_by.capitalize()}" if requested_by else ""}

    embed_file : Optional[discord.File] = None

    # Attach the disc GIF as a local file upload
    if CONST.EMBED_DISC_GIF_PATH:
        abs_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", CONST.EMBED_DISC_GIF_PATH)
        )
        if os.path.exists(abs_path):
            filename                  = os.path.basename(abs_path)
            embed_file                = discord.File(abs_path, filename = filename)
            footer_kwargs["icon_url"] = f"attachment://{filename}"

    if footer_kwargs["text"]:
        embed.set_footer(**footer_kwargs)

    # Timestamp
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

    return embed, embed_file

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
