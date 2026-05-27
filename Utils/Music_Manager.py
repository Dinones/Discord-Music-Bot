###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

import os
import sys
import random
import asyncio
import discord
from collections import deque
from discord.ext import commands
from typing import Deque, Dict, List, Optional

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Logs import save_exception_to_txt
from Utils.Youtube import configure_ytdl, get_audio_player
from Utils.Song import Song_Item, resolve_song_stream_url, enrich_song_from_video
from Utils.Embed.Now_Playing_Updater import Now_Playing_Updater, _send_now_playing_message

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Music Manager'

###########################################################################################################################
###########################################################################################################################

class Music_Manager():
    def __init__(self):

        self.current_song    = None
        self.current_updater : Optional[Now_Playing_Updater] = None
        self.is_processing   = False

        self.queue          : Deque[Song_Item] = deque()
        self.played_queue   : Deque[Song_Item] = deque()
        self.priority_queue : Deque[Song_Item] = deque()

        # When using threading.Lock() with async functions, "return await ..." doesn't release the lock
        self.queues_lock = asyncio.Lock()

        configure_ytdl(self)

###########################################################################################################################
###########################################################################################################################

    async def enqueue_songs(self, songs: List[Song_Item]) -> int:

        """
        Append songs at the end of the standard queue.

        Args:
            songs (List[Song_Item]): Normalized song objects to enqueue.

        Returns:
            int: Queue size after insertion.
        """

        async with self.queues_lock:
            for song in songs:
                self.queue.append(song)

            return len(self.priority_queue) + len(self.queue)

###########################################################################################################################
###########################################################################################################################

    async def enqueue_priority_song(self, song: Song_Item) -> int:

        """
        Append a single song to the end of the priority queue.

        Args:
            song (Song_Item): Normalized song object to enqueue with priority.

        Returns:
            int: Priority queue size after insertion.
        """

        async with self.queues_lock:
            self.priority_queue.append(song)
            return len(self.priority_queue)

###########################################################################################################################
###########################################################################################################################

    async def reserve_processing(self) -> bool:

        """
        Mark queue processing as busy if no worker is currently active.

        Returns:
            bool: True if caller must start a worker, False otherwise.
        """

        async with self.queues_lock:
            if self.is_processing:
                return False

            self.is_processing = True
            return True

###########################################################################################################################
###########################################################################################################################

    async def release_processing(self) -> None:

        """
        Mark queue processing as idle and clear current song.
        """

        async with self.queues_lock:
            self.is_processing = False
            self.current_song = None

###########################################################################################################################
###########################################################################################################################

    async def pop_next_song(self) -> Optional[Song_Item]:

        """
        Pop next song from priority queue first, then standard queue.

        Returns:
            Optional[Song_Item]: Next song to play, or None if queue is empty.
        """

        async with self.queues_lock:
            if self.priority_queue:
                song = self.priority_queue.popleft()
            elif self.queue:
                song = self.queue.popleft()
            else:
                return None

            self.current_song = song
            return song

###########################################################################################################################
###########################################################################################################################

    async def push_priority_song_front(self, song: Song_Item) -> int:

        """
        Reinsert a song at the front of the priority queue so it plays next.

        Args:
            song (Song_Item): Song to prepend to the priority queue.

        Returns:
            int: Priority queue size after insertion.
        """

        async with self.queues_lock:
            self.priority_queue.appendleft(song)
            return len(self.priority_queue)

###########################################################################################################################
###########################################################################################################################

    async def prepare_back_playback(self, previous_song: Song_Item, current_song: Optional[Song_Item]) -> None:

        """
        Atomically set up the priority queue for a back navigation: insert the previous song at the
        front, re-queue the current song directly behind it, and clear the current_song sentinel so the
        playback worker skips mark_song_played for the interrupted song.

        Args:
            previous_song (Song_Item): Song to play next, inserted at position 0.
            current_song (Optional[Song_Item]): Song currently playing or paused, re-queued at position 1.
                Pass None when the bot is idle.

        Returns:
            None
        """

        async with self.queues_lock:
            if current_song is not None:
                self.priority_queue.appendleft(current_song)
            self.priority_queue.appendleft(previous_song)
            self.current_song = None

###########################################################################################################################
###########################################################################################################################

    async def prepare_rewind_playback(self, song: Song_Item) -> None:

        """
        Atomically insert a song at the front of the priority queue and clear current_song
        so the interrupted song is not recorded in the played history.

        Args:
            song (Song_Item): Song to play next, typically a copy of the current song with
                seek_offset set to the desired playback position in seconds.

        Returns:
            None
        """

        async with self.queues_lock:
            self.priority_queue.appendleft(song)
            self.current_song = None

###########################################################################################################################

    async def pop_last_played_song(self) -> Optional[Song_Item]:

        """
        Pop and return the most recently played song from the played history.

        Returns:
            Optional[Song_Item]: Last played song, or None if the played queue is empty.
        """

        async with self.queues_lock:
            if not self.played_queue:
                return None

            return self.played_queue.pop()

###########################################################################################################################
###########################################################################################################################

    async def push_song_front(self, song: Song_Item) -> None:

        """
        Reinsert a song at the beginning of the standard queue.

        Args:
            song (Song_Item): Song to prepend.
        """

        async with self.queues_lock:
            self.queue.appendleft(song)
            self.current_song = None

###########################################################################################################################
###########################################################################################################################

    async def mark_song_played(self, song: Song_Item) -> None:

        """
        Track a song as played.

        Args:
            song (Song_Item): Played song payload.
        """

        async with self.queues_lock:
            self.played_queue.append(song)
            self.current_song = None

###########################################################################################################################
###########################################################################################################################

    async def clear_all_queues(self) -> None:

        """
        Clear standard, priority and played queues, and reset current song.
        """

        async with self.queues_lock:
            self.queue.clear()
            self.priority_queue.clear()
            self.played_queue.clear()
            self.current_song = None

###########################################################################################################################
###########################################################################################################################

    async def shuffle_normal_queue(self) -> int:

        """
        Shuffle only the standard queue in-place.

        Returns:
            int: Number of songs present in the standard queue.
        """

        async with self.queues_lock:
            queue_size = len(self.queue)
            if queue_size < 2:
                return queue_size

            queue_items = list(self.queue)
            random.shuffle(queue_items)
            self.queue.clear()
            self.queue.extend(queue_items)
            return queue_size

###########################################################################################################################
###########################################################################################################################

    async def peek_next_song(self) -> Optional[Song_Item]:

        """
        Return the next song that would be popped without removing it from the queue. Priority queue takes precedence over
        the normal queue.

        Returns:
            Optional[Song_Item]: Next song, or None if both queues are empty.
        """

        async with self.queues_lock:
            if self.priority_queue:
                return self.priority_queue[0]
            elif self.queue:
                return self.queue[0]
            return None

###########################################################################################################################
###########################################################################################################################

    async def get_full_queue_snapshot(self) -> tuple:

        """
        Return a consistent snapshot of the current song, priority queue, and normal queue under one lock.

        Returns:
            tuple: (current_song, list[Song_Item] priority, list[Song_Item] normal)
        """

        async with self.queues_lock:
            return (
                self.current_song,
                list(self.priority_queue),
                list(self.queue)
            )

###########################################################################################################################
###########################################################################################################################

    async def get_queue_size(self) -> int:

        """
        Return current standard queue size.

        Returns:
            int: Number of pending songs in standard queue.
        """

        async with self.queues_lock:
            return len(self.queue)

###########################################################################################################################
###########################################################################################################################

    async def get_queue_snapshot(self) -> List[Song_Item]:

        """
        Return a copy of queued songs.

        Returns:
            List[Song_Item]: Snapshot copy of standard queue songs.
        """

        async with self.queues_lock:
            return list(self.queue)

###########################################################################################################################
###########################################################################################################################

_GLOBAL_MUSIC_MANAGER = Music_Manager()

###########################################################################################################################
###########################################################################################################################

def get_music_manager() -> Music_Manager:

    """
    Return the shared global Music_Manager instance.

    Returns:
        Music_Manager: Singleton queue manager.
    """

    return _GLOBAL_MUSIC_MANAGER

###########################################################################################################################
###########################################################################################################################

async def _play_song_to_completion(
    voice_client : discord.VoiceClient,
    player       : discord.AudioSource,
    song         : Song_Item,
    message      : discord.Message,
    bot_loop     : asyncio.AbstractEventLoop,
    seek_offset  : int = 0
) -> None:

    """
    Start audio playback for a single song and block until it finishes. Creates the progress-bar updater, wires the
    voice-client after-callback to an asyncio Event so the coroutine can await completion without blocking the event loop,
    then tears down the updater once the song ends.

    Args:
        voice_client (discord.VoiceClient): Active voice connection to play audio on.
        player (discord.AudioSource): FFmpeg audio source returned by get_audio_player().
        song (Song_Item): Queue song item being played (used by the progress updater).
        message (discord.Message): The Now Playing embed message to keep updated.
        bot_loop (asyncio.AbstractEventLoop): The bot's running event loop, used to safely signal completion from the voice
            thread's after-callback.
        seek_offset (int): Seconds into the song where playback starts; passed to the updater so the progress bar
            initialises at the correct position (default 0).

    Returns:
        None
    """

    song_finished_event = asyncio.Event()

    def _after_playing(error: Optional[Exception]) -> None:
        if error:
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = MODULE_NAME,
                    action = "play queued song",
                    reason = error
                )
            )

        # Wake the awaiting coroutine from the correct thread
        bot_loop.call_soon_threadsafe(song_finished_event.set)

    voice_client.play(player, after = _after_playing)
    play_start_time = asyncio.get_running_loop().time()

    # Start the background task that edits the embed every _UPDATE_INTERVAL seconds
    updater = Now_Playing_Updater(message, song, voice_client, start_time = play_start_time, seek_offset = seek_offset)
    # Expose the updater on the manager so external commands (e.g. !rewind) can read elapsed time
    get_music_manager().current_updater = updater
    await updater.start()

    # Wait here until the after-callback fires (song ends or is stopped externally)
    await song_finished_event.wait()

    # Cancel the updater task cleanly so it does not outlive the song
    await updater.stop()
    get_music_manager().current_updater = None

    # Remove the now-playing embed so the channel stays clean before the next song's embed is posted
    try:
        await message.delete()
    except Exception as error:
        log_path = save_exception_to_txt(error = error, title = 'Now_Playing_Message_Delete')
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = MODULE_NAME,
                action = "delete now-playing message",
                reason = error
            )
        )

###########################################################################################################################
###########################################################################################################################

async def process_global_queue(context: commands.Context) -> None:

    """
    Process global queue songs sequentially until the queue is empty. Called as a background task by play-related commands.
    Only one worker runs at a time, enforced by reserve_processing / release_processing. Pre-fetches the next song's stream
    URL while the current song plays to minimize the gap between tracks.

    Args:
        context (commands.Context): Discord command context used to access the guild voice client, send Now Playing embeds,
            and report errors.

    Returns:
        None
    """

    music_manager = get_music_manager()
    # Carries the pre-fetched (song_ref, resolved_video) from the previous iteration so the next song starts playing
    # immediately without waiting for a fresh yt-dlp resolution
    prefetched : Optional[tuple] = None

    while True:
        # Priority queue is drained before the normal queue
        song = await music_manager.pop_next_song()
        if not song:
            await music_manager.release_processing()
            break

        voice_client = context.guild.voice_client if context.guild else None

        if voice_client is None or not voice_client.is_connected():
            # Bot was disconnected mid-queue: push the song back so it is not lost
            await music_manager.push_song_front(song)
            await music_manager.release_processing()
            break

        # Re-use the stream URL pre-fetched during the previous song's playback if it matches
        if prefetched is not None and prefetched[0] is song:
            resolved_video = prefetched[1]
        else:
            resolved_video = await resolve_song_stream_url(context, song)
        
        # Clear regardless so a failed pre-fetch does not carry over
        prefetched = None

        if not resolved_video:
            continue

        stream_url = str(resolved_video.get("url", "")).strip()
        if not stream_url:
            continue

        # Consume seek_offset so it does not persist into played history for future !back replays
        seek_offset = int(song.pop("seek_offset", 0) or 0)

        player = get_audio_player(stream_url, start_offset = seek_offset)
        if player is None:
            continue

        # Write the resolved YouTube URL and duration back into the song so embeds are accurate
        enrich_song_from_video(song, resolved_video)

        now_playing_msg = await _send_now_playing_message(context, song, seek_offset = seek_offset)

        # Start processing the next song while the current song is playing so there is no perceptible pause between tracks
        next_song = await music_manager.peek_next_song()
        prefetch_task : Optional[asyncio.Task] = None
        if next_song:
            prefetch_task = asyncio.create_task(resolve_song_stream_url(context, next_song))

        # Blocks here until the song current finishes or is skipped
        await _play_song_to_completion(voice_client, player, song, now_playing_msg, context.bot.loop, seek_offset = seek_offset)

        # Awaiting here covers the rare case where the previous song was very short and the pre-fetch is still in-flight
        if prefetch_task is not None:
            try:
                prefetch_result = await prefetch_task
                if prefetch_result:
                    prefetched = (next_song, prefetch_result)
            except Exception as error:
                log_path = save_exception_to_txt(error = error, title = 'Music_Manager_Prefetch')
                print(
                    STR.G_ACTION_NOT_DONE.format(
                        user   = MODULE_NAME,
                        action = "pre-fetch next song",
                        reason = error
                    )
                )

        if music_manager.current_song is song:
            await music_manager.mark_song_played(song)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    get_music_manager()
