###########################################################################################################################
#   Discord bot response message strings for error handling and user feedback.                                            #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################



###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

USER_SENDING_DM_TO_BOT = 'This command can only be used inside a server.'
USER_NOT_CONNECTED_TO_VC = 'Join a voice channel before using this command.'
USER_NOT_CONNECTED_TO_BOT_VC = 'Join the same voice channel as the bot before using `!disconnect`.'
BOT_MISSING_VOICE_DEPENDENCY = 'Voice support is not available. Install `PyNaCl` and restart the bot.'
BOT_COULD_NOT_CONNECT_TO_VC = 'I could not connect to your voice channel.'
BOT_NOT_CONNECTED_TO_VC = 'I am not connected to any voice channel.'
BOT_NOT_PLAYING_ANYTHING = 'I am not playing anything right now.'
BOT_ALREADY_PAUSED = 'Playback is already paused.'
BOT_NOT_PAUSED = 'Playback is not paused.'
UNKNOWN_COMMAND = 'The command `{command}` does not exist.'
SHUFFLE_DONE = 'Shuffled **{number}** songs in the normal queue.'
PLAY_COULD_NOT_FIND_SONGS = 'I could not find any playable songs for that input.'
PLAY_SONG_ADDED_TO_QUEUE = 'Added to queue: **{title}** (Queue size: **{size}**).'
PLAY_SONGS_ADDED_TO_QUEUE = 'Added **{number}** songs to queue (Queue size: **{size}**).'
PLAY_NOW_PLAYING = 'Now playing: **{title}**.'
BACK_NO_PREVIOUS_SONG = 'There is no previous song in the history.'
PLAYNEXT_SONG_ADDED_TO_PRIORITY_QUEUE = 'Added to priority queue: **{title}** (Priority queue size: **{size}**).'
PLAYNEXT_PLAYLIST_NOT_SUPPORTED = \
    'Playlists cannot be added with priority. Added **{number}** songs to the normal queue (Queue size: **{size}**).'
VOLUME_INVALID_ARGUMENT = 'Volume must be an integer number between **0** and **100**.'
VOLUME_CURRENT_VOLUME = 'Current volume: **{volume}%**.'
PING = 'Pong! Latency: **{latency} ms**.'
REWIND_INVALID_ARGUMENT = 'Rewind argument must be a positive integer number of seconds.'
BOT_STARTED = 'Bot is online and ready!'
QUEUE_FINISHED    = 'The karaoke has ended!'
AUTO_DISCONNECTED = 'Disconnected because alone in the voice channel for **{time}**.'
LYRICS_NOT_FOUND  = 'No lyrics found'
LYRICS_RETRIEVING = 'Retrieving lyrics...'
LYRICS_MUSIC      = '(Music)'
NO_PLAYLISTS_CONFIGURED = 'No playlists have been configured.'
PLAYLISTS_PANEL         = 'Select a playlist:'

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
