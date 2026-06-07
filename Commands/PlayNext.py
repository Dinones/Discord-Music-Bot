###########################################################################################################################
#   Implements the !playnext command, which adds a song to the front of the priority queue.                              #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Music_Manager import get_music_manager

from Commands.Resume import resume as resume_playback
from Commands.Connect import connect as connect_to_voice_channel
from Commands.Play import resolve_play_request
from Utils.Music_Manager import process_global_queue
from Utils.Reactions import send_reaction, remove_reaction

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

async def playnext(context: commands.Context, args: str, priority_front: bool = False) -> bool:

    """
    Queue a single song to the priority queue, or fall back to a shuffled normal enqueue for playlists.

    Args:
        context (commands.Context): Discord command context.
        args (str): Youtube URL, Spotify URL or text query. Empty string resumes paused playback.
        priority_front (bool): When True, insert the single song at the front of the priority queue instead of the end.

    Returns:
        bool: True if a single song was queued, False if a playlist was processed or the command returned early.
    """

    args = args.strip()
    if not args:
        await resume_playback(context)
        return False

    is_ready = await connect_to_voice_channel(context)

    if not is_ready:
        return False

    # Show loading indicator while the API call resolves the song
    await send_reaction(context.message, "⏳")

    songs_to_queue = await resolve_play_request(context, args)

    if not songs_to_queue:
        await send_reaction(context.message, "❌")
        await remove_reaction(context.message, "⏳", context.bot.user)
        await context.send(MSG.PLAY_COULD_NOT_FIND_SONGS)
        return False

    music_manager  = get_music_manager()
    is_single_song = len(songs_to_queue) == 1

    # Playlists are not supported in the priority queue; fall back to a shuffled normal enqueue instead
    if not is_single_song:
        queue_size = await music_manager.enqueue_songs(songs_to_queue)
        await music_manager.shuffle_normal_queue()

        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "playnext",
                result = f'Added {len(songs_to_queue)} songs to normal queue and shuffled (Total: {queue_size})'
            )
        )
        await context.send(
            MSG.PLAYNEXT_PLAYLIST_NOT_SUPPORTED.format(
                number = len(songs_to_queue),
                size   = queue_size
            )
        )

    else:
        # priority_front = True inserts before all other priority songs; False appends to the end
        if priority_front:
            priority_size = await music_manager.push_priority_song_front(songs_to_queue[0])
        else:
            priority_size = await music_manager.enqueue_priority_song(songs_to_queue[0])

        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "playnext",
                result = \
                    f'Added "{songs_to_queue[0].get("title", "Unknown title")}" to priority queue ' +\
                    f'(Priority size: {priority_size})'
            )
        )

        song  = songs_to_queue[0]
        title = song.get("title", "Unknown title")
        url   = song.get("playback_query", "") or song.get("spotify_url", "")

        await context.send(
            MSG.PLAYNEXT_SONG_ADDED_TO_PRIORITY_QUEUE.format(
                title = f"[{title}]({url})" if url else title,
                size  = priority_size
            )
        )

    # Only the first caller starts the playback worker; concurrent callers only enqueue
    should_start_processing = await music_manager.reserve_processing()

    await send_reaction(context.message, "✅")
    await remove_reaction(context.message, "⏳", context.bot.user)

    if should_start_processing:
        context.bot.loop.create_task(process_global_queue(context))

    return is_single_song

###########################################################################################################################
###########################################################################################################################

def register_playnext_command(bot: commands.Bot) -> None:

    """
    Register the "!playnext" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "playnext", aliases = ["playn"])
    async def playnext_command(context: commands.Context, *, args: str = "") -> None:

        """
        Add a single song to the priority queue, or add a playlist to the normal queue with shuffle.
        """

        await playnext(context, args)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
