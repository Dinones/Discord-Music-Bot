###########################################################################################################################
#   Central configuration constants, API URLs, timeouts, and environment-specific settings.                              #
###########################################################################################################################

###########################################################################################################################
#####################################################     DISCORD     #####################################################
###########################################################################################################################

BOT_PREFIX = '!'
EMBED_DISC_GIF_PATH = 'Media/Others/Spinning_Disc.gif'
# Options: "Playing", "Watching", "Streaming", "Listening", "Competing"
BOT_ACTIVITY_TYPE = 'Listening'
# Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" or empty string to disable all
LOGGING_LEVEL = ''
# Seconds the bot waits alone in a voice channel before disconnecting automatically
AUTO_DISCONNECT_TIMEOUT_SECONDS = 60 * 5

###########################################################################################################################
#####################################################     SECRETS     #####################################################
###########################################################################################################################

AWS_REGION  = "eu-west-1"
SECRET_NAME = "discord_music_bot_secrets"
YT_COOKIES_SECRET_NAME = 'discord_music_bot_youtube_cookies'

S3_EXTRA_COMMANDS_PREFIX = "extra-commands/"

###########################################################################################################################
#####################################################     YOUTUBE     #####################################################
###########################################################################################################################

YT_COOKIES_FILE_PATH = 'Media/Others/Youtube_Cookies.txt'

###########################################################################################################################
#####################################################     SPOTIFY     #####################################################
###########################################################################################################################

SPOTIFY_DEFAULT_MARKET = "ES"
SPOTIFY_REQUEST_TIMEOUT = 10
SPOTIFY_TOKEN_EXPIRATION_BUFFER_SECONDS = 60

###########################################################################################################################
######################################################     TESTS     ######################################################
###########################################################################################################################

TESTING_AUTHOR_NAME = 'Dinones'

TESTING_YOUTUBE_LINK = 'https://www.youtube.com/watch?v=7dSMNXg-QEQ'
TESTING_YOUTUBE_QUERY = 'La bbesita bb lean'
TESTING_MP3_DOWNLOAD_OUTPUT_PATH = 'Media/Audios/'

TESTING_LYRICS_TITLE    = 'LEAN'
TESTING_LYRICS_ARTIST   = 'Superiority'
TESTING_LYRICS_DURATION = 0

TESTING_SPOTIFY_SONG_LINK = 'https://open.spotify.com/track/5DoLhdU27owX1NMrKLUbUl'
TESTING_SPOTIFY_PLAYLIST_LINK = 'https://open.spotify.com/playlist/0PenuWAdyz6JIT1nmEl77F'
TESTING_SPOTIFY_ALBUM_LINK = 'https://open.spotify.com/album/3RQQmkQEvNCY4prGKE6oc5'

###########################################################################################################################
######################################################     LRCLIB     ######################################################
###########################################################################################################################

LRCLIB_API_BASE_URL     = 'https://lrclib.net/api'
LRCLIB_REQUEST_TIMEOUT  = 15

###########################################################################################################################
######################################################     FILTERS     ####################################################
###########################################################################################################################

GENRE_FILTERS = {
    "🥘 Catalan" : [
        "31 FAM", "Auxili", "Buhos", "Búhos", "Doctor Prats", "Els Amics de les Arts", "Els Catarres", "Els Pets",
        "Figa Flawas", "Joan Dausà", "Julieta", "La Fúmiga", "La Pegatina", "Lildami", "Oques Grasses", "Sopa de Cabra",
        "Sopa de Cabra", "Stay Homas", "Teràpia de Shock", "The Tyets", "Triquell", "Txarango", "Zoo",
    ],

    "💃🏽 Spanish (REM)" : [
        "Alejandro Sanz", "Álex Ubago", "Amaia Montero", "Amaral", "Antonio Orozco", "Carlos Baute", "Celtas Cortos",
        "Chenoa", "Dani Fernández", "Dani Martín", "David Bustamante", "David DeMaría", "David Otero", "Dvicio",
        "Efecto Mariposa", "Efecto Pasillo", "El Canto del Loco", "El Sueño de Morfeo", "Estopa", "Extremoduro",
        "Fito & Fitipaldis", "Fito y Fitipaldis", "Hombres G", "Jarabe de Palo", "Joaquín Sabina", "Juanes",
        "La La Love You", "La Oreja de Van Gogh", "La Pegatina", "La Quinta Estación", "La Quinta Estacion", "Leiva",
        "Los Rodríguez", "Los Rodriguez", "Macaco", "Maldita Nerea", "Manuel Carrasco", "Melendi", "Morat", "Nena Daconte",
        "Pablo Alborán", "Pablo López", "Pereza", "Pignoise", "Taburete", "Marlena", "Jennifer López", "Jennifer Lopez",
        "Julieta Venegas", "Malú", "Los Ronaldos", "Chambao", "Sergio Dalma", "Paulina Rubio", "Miguel Bosé",
        "Manolo García", "Manolo Garcia", "Duncan Dhu", "Diego Torres", "Fangoria", "Nek", "Alaska", "Despistaos", ""
    ],

    "🪩 Reggaeton": [
        "Ana Mena", "Andy Rivera", "Anuel AA", "Arcángel", "Bad Bunny", "Bad Gyal", "Becky G", "Bizarrap", "C. Tangana",
        "Calle 13", "Chimbala", "Daddy Yankee", "Dani Flow", "Danny Ocean", "De La Ghetto", "Dellafuente", "Don Omar",
        "Duki", "El Alfa", "Eladio Carrión", "Emilia", "Enrique Iglesias", "Farruko", "Feid", "J Balvin", "Jhay Cortez",
        "Jhayco", "Juan Magán", "Karol G", "Kidd Keo", "Lirico En La Casa", "Lola Índigo", "Maluma", "Manuel Turizo",
        "María Becerra", "Morad", "Mozart La Para", "Myke Towers", "Nicky Jam", "Nicki Nicole", "Omar Montes",
        "Osmani García", "Ovy On The Drums", "Ozuna", "Paulo Londra", "Piso 21", "Pitbull", "Quevedo", "Rauw Alejandro",
        "Rels B", "Residente", "Rosalía", "Ryan Castro", "RVFV", "Saiko", "Sech", "Sebastián Yatra", "Tainy", "Tiago PZK",
        "Tini", "Trueno", "Yandel", "Eminem", "Dany Paz", "El Villano", "Marshmello", "Don Patricio", "Martin Garrix",
    ]
}
