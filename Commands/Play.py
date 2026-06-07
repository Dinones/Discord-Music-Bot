###########################################################################################################################
#   Implements the !play command, which searches for and queues a song from YouTube or Spotify.                          #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
from discord.ext import commands
from typing import List

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Music_Manager import get_music_manager, process_global_queue
from Utils.Spotify import search_spotify_songs, is_spotify_url
from Utils.Youtube import search_youtube_video
from Utils.Song import Song_Item, build_song_item_from_youtube, build_song_item_from_spotify_track
from Commands.Resume import resume as resume_playback
from Commands.Connect import connect as connect_to_voice_channel
from Utils.Reactions import send_reaction, remove_reaction

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = "Play"

###########################################################################################################################
###########################################################################################################################

async def resolve_play_request(context: commands.Context, args: str) -> List[Song_Item]:

    """
    Resolve a play command input into a list of normalized queue song items. Handles Spotify URLs (single track, playlist,
    or album), YouTube URLs, and plain text search queries.

    Args:
        context (commands.Context): Discord command context.
        args (str): Original !play argument string.

    Returns:
        List[Song_Item]: List of normalized song items ready to enqueue, or an empty list on failure.
    """

    music_manager  = get_music_manager()
    songs_to_queue : List[Song_Item] = []

    if is_spotify_url(args):

        spotify_songs = await search_spotify_songs(context.message, args)

        for spotify_song in spotify_songs:
            queue_song = build_song_item_from_spotify_track(spotify_song, context.author.name)
            if queue_song:
                songs_to_queue.append(queue_song)

        return songs_to_queue

    video = await search_youtube_video(music_manager, context.message, args)

    if not video:
        return songs_to_queue

    queue_song = build_song_item_from_youtube(video, context.author.name)
    if queue_song:
        songs_to_queue.append(queue_song)

    return songs_to_queue

###########################################################################################################################
###########################################################################################################################

async def play(context: commands.Context, args: str, shuffle: bool = False, reverse: bool = False) -> None:

    """
    Queue songs and start playback.

    Args:
        context (commands.Context): Discord command context.
        args (str): Youtube URL, Spotify URL or text query. Empty string resumes paused playback.
        shuffle (bool): When True, shuffle the queue after enqueuing and before playback starts.
        reverse (bool): When True, reverse the resolved song list before enqueuing.

    Returns:
        None
    """

    args = args.strip()
    if not args:
        await resume_playback(context)
        return

    is_ready = await connect_to_voice_channel(context)

    if not is_ready:
        return

    # Show loading indicator while the API call resolves the song
    await send_reaction(context.message, "⏳")

    songs_to_queue = await resolve_play_request(context, args)
    if not songs_to_queue:
        await send_reaction(context.message, "❌")
        await remove_reaction(context.message, "⏳", context.bot.user)
        await context.send(MSG.PLAY_COULD_NOT_FIND_SONGS)
        return

    if reverse:
        songs_to_queue = list(reversed(songs_to_queue))

    music_manager = get_music_manager()
    # Enqueue first, then optionally shuffle, then reserve queue worker in a race-safe way
    queue_size = await music_manager.enqueue_songs(songs_to_queue)

    if shuffle:
        await music_manager.shuffle_normal_queue()

    should_start_processing = await music_manager.reserve_processing()

    # Report queue update to the user
    if len(songs_to_queue) == 1:
        song  = songs_to_queue[0]
        title = song.get("title", "Unknown title")
        url   = song.get("playback_query", "") or song.get("spotify_url", "")
        await context.send(
            MSG.PLAY_SONG_ADDED_TO_QUEUE.format(
                title = f"[{title}]({url})" if url else title,
                size  = queue_size
            )
        )
        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "queue and play songs",
                result = f'Added 1 song to queue (Total: {queue_size})'
            )
        )
    else:
        await context.send(
            MSG.PLAY_SONGS_ADDED_TO_QUEUE.format(
                number = len(songs_to_queue),
                size   = queue_size
            )
        )
        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "queue and play songs",
                result = f'Added {len(songs_to_queue)} songs to queue (Total: {queue_size})'
            )
        )

    await send_reaction(context.message, "✅")
    await remove_reaction(context.message, "⏳", context.bot.user)

    if should_start_processing:
        # Only the first caller starts the playback worker; next callers only enqueue
        context.bot.loop.create_task(process_global_queue(context))

###########################################################################################################################
###########################################################################################################################

def register_play_command(bot: commands.Bot) -> None:

    """
    Register the "!play" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.

    Returns:
        None
    """

    @bot.command(name = "play")
    async def play_command(context: commands.Context, *, args: str = "") -> None:

        """
        Queue and play songs from Youtube URL, Spotify URL or text query.
        """

        await play(context, args)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
