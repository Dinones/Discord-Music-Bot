###########################################################################################################################
#   Builds the queue Discord embed listing the current, priority, and normal queue songs.                                #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import discord
from typing import List, Optional

from Utils.Song import Song_Item

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_EMBED_COLOR = discord.Color.from_rgb(195, 0, 0)
_MAX_SONGS   = 8

###########################################################################################################################
###########################################################################################################################

def _linked_title(song: Song_Item) -> str:

    title = song.get("title", "Unknown")
    # Prefer the resolved YouTube URL; fall back to Spotify URL when the song hasn't been played yet
    url   = song.get("playback_query", "") or song.get("spotify_url", "")

    return f"[{title}]({url})" if url else title

###########################################################################################################################
###########################################################################################################################

def build_queue_embed(
    current_song   : Optional[Song_Item],
    priority_queue : List[Song_Item],
    normal_queue   : List[Song_Item]
) -> discord.Embed:

    """
    Build a Discord embed displaying the current song and upcoming queue.

    Args:
        current_song (Optional[Song_Item]): Song currently playing or paused, or None.
        priority_queue (List[Song_Item]): Priority queue snapshot.
        normal_queue (List[Song_Item]): Normal queue snapshot.

    Returns:
        discord.Embed: Ready-to-send embed object.
    """

    embed = discord.Embed(color = _EMBED_COLOR)
    total = len(priority_queue) + len(normal_queue)

    # Now Playing section
    if current_song:
        value  = _linked_title(current_song)
        embed.add_field(name = "⭐  **Now Playing**", value = f'**>>⠀{value}**', inline = False)
        if total > 0:
            # Blank spacer field for visual separation between Now Playing and Up Next
            embed.add_field(name = "⠀", value = "", inline = False)

    # Up Next section
    if total > 0:
        lines = []
        shown = 0

        # Priority songs are shown first with a star marker
        for index, song in enumerate(priority_queue):
            if shown >= _MAX_SONGS:
                break
            lines.append(f"{index + 1}. ✨ **{_linked_title(song)}**")
            shown += 1

        # Normal queue continues the numbering after priority songs
        pq_len = len(priority_queue)
        for index, song in enumerate(normal_queue):
            if shown >= _MAX_SONGS:
                break
            lines.append(f"{pq_len + index + 1}. **{_linked_title(song)}**")
            shown += 1

        # Append overflow notice when the queue exceeds the display limit
        remaining = total - shown
        value     = "\n".join(lines)
        if remaining > 0:
            value += f"\n\n*... and {remaining} more song{'s' if remaining != 1 else ''}*"

        embed.add_field(name = "📃  **Up Next**", value = value, inline = False)

    # Footer
    footer = f"{total} {'song' if total == 1 else 'songs'} in queue"
    embed.set_footer(text = footer)

    return embed

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
