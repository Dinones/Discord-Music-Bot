###########################################################################################################################
#   Picks and plays a random MP3 intro clip from Media/Audios/Playable/ when the bot first joins a voice channel.        #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import random
import asyncio
from typing import Optional

import discord
from discord import PCMVolumeTransformer, FFmpegPCMAudio

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME   = "Audio Intro"
_PLAYABLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Media", "Audios", "Playable"))

###########################################################################################################################
###########################################################################################################################

def pick_random_intro() -> Optional[str]:

    """
    Return a random MP3 file path from the Playable directory, or None if the folder is missing or empty.

    Returns:
        Optional[str]: Absolute path to a randomly selected MP3, or None.
    """

    if not os.path.isdir(_PLAYABLE_DIR):
        return None

    mp3_files = [
        os.path.join(_PLAYABLE_DIR, f)
        for f in os.listdir(_PLAYABLE_DIR)
        if f.lower().endswith(".mp3")
    ]

    if not mp3_files:
        return None

    return random.choice(mp3_files)

###########################################################################################################################
###########################################################################################################################

async def play_intro_audio(voice_client: discord.VoiceClient) -> None:

    """
    Play a randomly selected intro clip through the voice client and wait for it to finish.
    Does nothing if the Playable folder is empty or has no MP3 files.

    Args:
        voice_client (discord.VoiceClient): Active voice connection to play audio on.

    Returns:
        None
    """

    path = pick_random_intro()
    if path is None:
        return

    print(
        STR.G_ACTION_DONE.format(
            user   = MODULE_NAME,
            action = "play intro audio",
            result = os.path.basename(path)
        )
    )

    loop = asyncio.get_running_loop()
    done = asyncio.Event()

    def _after(error: Optional[Exception]) -> None:
        loop.call_soon_threadsafe(done.set)

    player        = PCMVolumeTransformer(FFmpegPCMAudio(path))
    player.volume = 1.0
    voice_client.play(player, after = _after)
    await done.wait()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
