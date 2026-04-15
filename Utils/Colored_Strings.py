###########################################################################################################################
#  Who doesn't like colors? Just a script to print with colors in the terminal making it more visual.                     #
###########################################################################################################################

###########################################################################################################################
####################################################     CONSTANTS     ####################################################
###########################################################################################################################

SPECIAL = {
    "Default"       : '0',
    "Bold"          : '1',
    "Italics"       : '3',
    "Underlined"    : '4',
    "Strikethrough" : '9'
}

COLORS = {
    "Black"     : '30',
    "Red"       : '31',
    "Green"     : '32',
    "Yellow"    : '33',
    "Blue"      : '34',
    "Magenta"   : '35',
    "Cyan"      : '36',
    "White"     : '37',

    "DarkGray"      : '90',
    "LightRed"      : '91',
    "LightGreen"    : '92',
    "LightYellow"   : '93',
    "LightBlue"     : '94',
    "LightMagenta"  : '95',
    "LightCyan"     : '96',
}

BACKGROUND = {
    "Black"     : '40',
    "Red"       : '41',
    "Green"     : '42',
    "Yellow"    : '43',
    "Blue"      : '44',
    "Magenta"   : '45',
    "Cyan"      : '46',
    "White"     : '47',
}

RESET_FORMAT = '\033[0;m'

INFO = f'\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[+] {RESET_FORMAT}'
CORRECT = f'\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[>] {RESET_FORMAT}'
WARN = f'\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[!] {RESET_FORMAT}'
ERROR = f'\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[X] {RESET_FORMAT}'

###########################################################################################################################
#####################################################     GENERAL     #####################################################
###########################################################################################################################

G_COULD_NOT_GET_AWS_SECRETS = \
    f'{ERROR}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{module}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]};{SPECIAL["Bold"]}mCould not get AWS secrets: {RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]}m{"{error}"} {RESET_FORMAT}'

G_BOT_INITIALIZED = \
    f'{CORRECT}\033[{SPECIAL["Bold"]};{COLORS["Green"]}mBot initialized successfully!{RESET_FORMAT}'

G_ACTION_DONE = \
    f'{CORRECT}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{user}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mTried to {"{action}"}: {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m{"{result}"}{RESET_FORMAT}'

G_ACTION_NOT_DONE = \
    f'{WARN}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{user}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]};{SPECIAL["Bold"]}mTried to {"{action}"}: {RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]}m{"{reason}"}{RESET_FORMAT}'

G_UNKNOWN_COMMAND_USED = \
    f'{WARN}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{user}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mTried to use a command that does not exist: {RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]}m{"{command}"}{RESET_FORMAT}'

G_INVALID_PATH_ERROR = \
    f'{ERROR}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{module}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]};{SPECIAL["Bold"]}mInvalid path: {RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]}m{"{path}"}{RESET_FORMAT}'

G_SONG_PLAYER_ERROR = \
    f'{ERROR}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{module}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]};{SPECIAL["Bold"]}mSong player error: {RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]}m{"{error}"}{RESET_FORMAT}'

###########################################################################################################################
######################################################     MENU     #######################################################
###########################################################################################################################

M_MENU = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{module}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mSelection Menu:{RESET_FORMAT}'

M_MENU_OPTION = \
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}m    [{"{index}"}] {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]}m{"{option}"}{RESET_FORMAT}'

M_OPTION_SELECTION = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{module}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mSelect an option: {RESET_FORMAT}'

M_INVALID_OPTION = \
    f'{ERROR}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{module}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]};{SPECIAL["Bold"]}mInvalid option: {RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]}mExiting the program...{RESET_FORMAT}'

M_SELECTED_OPTION = \
    f'{CORRECT}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{module}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]};{SPECIAL["Bold"]}mOption {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m{"{option}"}{RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]};{SPECIAL["Bold"]}m selected: {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m{"{action} "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m{"{path}"}{RESET_FORMAT}'

###########################################################################################################################
##################################################     MUSIC MANAGER     ##################################################
###########################################################################################################################

MM_BACKGOUND_PROCESS_SONG_THREAD_INITIALIZED = \
    f'{CORRECT}\033[{SPECIAL["Bold"]};{COLORS["Green"]}mProcess queue songs thread initialized successfully!{RESET_FORMAT}'

MM_SONG_LOADED_NORMAL = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{user}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mAdded a song to the end of the queue: {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]}m{"{title}"}{RESET_FORMAT}'

MM_SONG_LOADED_PRIORITY = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{user}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mAdded a song to the priority queue: {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]}m{"{title}"}{RESET_FORMAT}'

MM_SONG_LOADED_NOW = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{user}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mSkipped the current song to play: {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]}m{"{title}"}{RESET_FORMAT}'

MM_PLAYLIST_LOADED_NORMAL = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{user}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mAdded {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]}m{"{number}"}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}m songs to the end of the queue{RESET_FORMAT}'

###########################################################################################################################
#####################################################     YOUTUBE     #####################################################
###########################################################################################################################

YT_COOKIES_FILE_NOT_FOUND = \
    f'{WARN}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[Youtube] {RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]};{SPECIAL["Bold"]}mCould not load Youtube cookies file: {RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]}mFile does not exist {RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]}m"{"{path}"}"{RESET_FORMAT}'

YT_AUDIO_DOWNLOADED = \
    f'{CORRECT}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[Youtube] {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]};{SPECIAL["Bold"]}mFile downloaded {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m({"{seconds}"}s){RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]};{SPECIAL["Bold"]}m: {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m{"{output_path}"}{RESET_FORMAT}'

YT_VIDEO_FOUND = \
    f'{CORRECT}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[Youtube] {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]};{SPECIAL["Bold"]}mVideo found {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m({"{seconds}"}s){RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]};{SPECIAL["Bold"]}m: {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m{"{title}"}{RESET_FORMAT}'

YT_INVALID_YOUTUBE_INPUT = \
    f'{WARN}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{user}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]};{SPECIAL["Bold"]}mTried to play something from Youtube: {RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]}m{"{reason}"}{RESET_FORMAT}'

YT_COULD_NOT_UPDATE_SPOTIFY_SONG = \
    f'{WARN}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[Youtube] {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mCould not update a Spotify with Youtube info: {RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]}m{"{reason}"}{RESET_FORMAT}'

###########################################################################################################################
#####################################################     SPOTIFY     #####################################################
###########################################################################################################################

SP_COULD_NOT_GET_TOKEN = \
    f'{WARN}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[Spotify] {RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]};{SPECIAL["Bold"]}mCould not get Spotify access token{RESET_FORMAT}'

SP_SONGS_FOUND = \
    f'{CORRECT}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[Spotify] {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]};{SPECIAL["Bold"]}mFound {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m{"{number}"} {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]};{SPECIAL["Bold"]}msong(s) {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m({"{seconds}"}s){RESET_FORMAT}'

###########################################################################################################################
##################################################     EVENT HANDLER     ##################################################
###########################################################################################################################

EH_COMMAND_LOADED = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Blue"]}mCommand {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]}m{"{command_name}"}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}m loaded {RESET_FORMAT}'+\
    f'\033[{COLORS["Magenta"]};{SPECIAL["Bold"]}m{"({index}/{total_lenght})"}{RESET_FORMAT}'

EH_STT_TRANSCRIPTION = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Blue"]}mTranscription: {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]}m{"{transcription}"}{RESET_FORMAT}'

###########################################################################################################################
######################################################     LOGS     #######################################################
###########################################################################################################################

LOG_CREATED = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[Logs] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mA new log has been generated: {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]}m{"{log_path}"}{RESET_FORMAT}'

###########################################################################################################################
#####################################################     COOKIES     #####################################################
###########################################################################################################################

CK_COULD_NOT_GET_YT_COOKIES = \
    f'{WARN}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[Cookies] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]};{SPECIAL["Bold"]}mCould not retrieve cookies from AWS: {RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]}m{"{error}"}{RESET_FORMAT}'

CK_YT_COOKIES_EMPTY = \
    f'{WARN}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[Cookies] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Yellow"]};{SPECIAL["Bold"]}mYoutube cookies retrieved from AWS are empty{RESET_FORMAT}'

CK_RETRIEVING_YT_COOKIES_FROM_AWS = \
    f'{INFO}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[Cookies] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]};{SPECIAL["Bold"]}mCould not find local Youtube cookies file: {RESET_FORMAT}'+\
    f'\033[{COLORS["Blue"]}mTrying to retrieve them from AWS{RESET_FORMAT}'

CK_RETRIEVED_YT_COOKIES_FROM_AWS = \
    f'{CORRECT}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[Cookies] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]};{SPECIAL["Bold"]}mSuccessfully retrieved Youtube cookies from AWS: {RESET_FORMAT}'+\
    f'\033[{COLORS["Green"]}m{"{path}"}{RESET_FORMAT}'