<h1 align="center">
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Music.svg" width="30px" align="top"/>ㅤDiscord Music Botㅤ<img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Music.svg" width="30px" align="top"/>
</h1>

<p align="center">
    Play YouTube and Spotify music in Discord with queue controls, synced lyrics, playlist buttons, and listening stats.
</p>

<p align="center">
    <a href="#key-features">Key Features</a> •
    <a href="#screenshots">Screenshots</a> •
    <a href="#python-setup">Setup</a> •
    <a href="Documentation/Discord_Bot_Setup.md">Discord App Setup</a> •
    <a href="Documentation/Cloud_Setup.md">AWS Setup</a>
</p>

<br>

<h2 id="key-features">
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Star.svg" width="30px" align="top"/>
    ⠀Key Features
</h2>

<p>
    <p>
        &emsp; <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Music.svg" width="20px" align="center"/>⠀Play music from YouTube links, YouTube searches, Spotify tracks, Spotify albums, and Spotify playlists. <br>
    </p><p>
        &emsp; <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Clipboard.svg" width="20px" align="center"/>⠀Manage playback with queue, priority queue, skip, back, pause, resume, and more controls. <br>
    </p>
    <p>
        &emsp; <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Chat.svg" width="20px" align="center"/>⠀Show synced lyrics while playing the music. <br>
    </p>
    <p>
        &emsp; <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Monitor.svg" width="20px" align="center"/>⠀Track listening stats, user activity, skipped songs, sessions, streaks, and top requests. <br>
    </p>
    <p>
        &emsp; <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Key.svg" width="20px" align="center"/>⠀Load Discord, Spotify, YouTube cookies, and optional private commands from AWS. <br>
    </p>
</p>

<br>

<h2 id="screenshots">
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Camera.svg" width="30px" align="top"/>
    ⠀Screenshots
</h2>

<h3>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Music.svg" width="22px" align="top"/>
    ⠀Now Playing
</h3>

<p align="center">
    <img src="Media/Others/Now_Playing_Example.png" alt="Now Playing message example" width="40%" style="border-radius: 15px;">
</p>

<br>

<h3>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Keyboard.svg" width="22px" align="top"/>
    ⠀Commands
</h3>

<p align="center">
    <img src="Media/Others/Commands_Example.png" alt="Commands help example" width="65%" style="border-radius: 15px;">
</p>

<br>

<h3>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Monitor.svg" width="22px" align="top"/>
    ⠀Stats Dashboard
</h3>

<p align="center">
    <img src="Media/Others/Stats_Example.jpeg" alt="Stats dashboard example" width="90%" style="border-radius: 15px;">
</p>

<br>

<h2 id="python-setup">
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Python.svg" width="30px" align="top"/>
    ⠀Python Setup
</h2>

This project requires **Python 3.12**.

<h3>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Windows.svg" width="22px" align="top"/>
    ⠀Windows Environment
</h3>

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r Requirements.txt
```

<h3>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Linux.svg" width="22px" align="top"/>
    ⠀Linux Environment
</h3>

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r Requirements.txt
```

<br>

<h2>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Gear%201.svg" width="30px" align="top"/>
    ⠀FFmpeg and Playwright Installation
</h2>

This bot requires `ffmpeg` to play audio and `playwright` to visualize stats.

<h3>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Windows.svg" width="22px" align="top"/>
    ⠀Windows Environment
</h3>

Run a powershell as administrator and run:

```powershell
choco install ffmpeg -y
playwright install chromium
```

<h3>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Linux.svg" width="22px" align="top"/>
    ⠀Linux Environment
</h3>

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
playwright install chromium
playwright install-deps chromium
```

<br>

<h2>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Discord.svg" width="30px" align="top"/>
    ⠀Discord App Setup
</h2>

Create the Discord application, configure the bot token/intents, and install it into your server using [`Documentation/Discord_Bot_Setup.md`](Documentation/Discord_Bot_Setup.md).

<br>

<h2>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Lock.svg" width="30px" align="top"/>
    ⠀AWS Setup
</h2>

The bot reads its secrets (Discord token, Spotify credentials, etc.) from AWS Secrets Manager. Follow the steps in [`Documentation/Cloud_Setup.md`](Documentation/Cloud_Setup.md) to provision the required AWS resources and fill the secret values.

If AWS Secrets Manager cannot be reached (no AWS access configured), the bot automatically falls back to reading the same keys from environment variables, so it can also run entirely off a `.env` file (see <a href="#running-without-aws">Running Without AWS</a>).

> [!NOTE]
> **Why AWS?** Strictly speaking, this project didn't need AWS at all: a gitignored `.env` file could have held every secret on its own. AWS Secrets Manager and S3 were used here to get hands-on practice with AWS, and because I run this bot from different computers, so keeping secrets in one central place is convenient.
>
> Once that learning goal was met, staying fully dependent on AWS stopped making sense for a small personal project. That's why `.env` support was added as a proper fallback rather than an afterthought (see [Running Without AWS](#running-without-aws)).

<br>

<h2>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Gear%202.svg" width="30px" align="top"/>
    ⠀Environment Configuration
</h2>

Create a `.env` file in the project root to configure local settings. This file is gitignored and never committed.

```env
BOT_ENV=dev
```

| Variable  | Values          | Default | Description                                       |
|-----------|-----------------|---------|---------------------------------------------------|
| `BOT_ENV` | `dev` \| `prod` | `dev`   | Selects which Discord token and channel to use.   |

<br>

<h3 id="running-without-aws">
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Gear%203.svg" width="22px" align="top"/>
    ⠀Running Without AWS
</h3>

When there is no AWS access, add the secret keys directly to `.env` and the bot will use them instead:

```env
BOT_ENV=dev

DISCORD_MUSIC_BOT_TOKEN_DEV  = ""
DISCORD_MUSIC_BOT_TOKEN_PROD = ""

SPOTIFY_CLIENT_ID     = ""
SPOTIFY_CLIENT_SECRET = ""

BOT_ACTIVITY_NAME         = ""
DISCORD_SERVER_NAME       = ""
DISCORD_TEXT_CHANNEL_DEV  = ""
DISCORD_TEXT_CHANNEL_PROD = ""

S3_EXTRA_COMMANDS_BUCKET = 
SPOTIFY_PLAYLISTS        = [{"name": "", "url": "https://open.spotify.com/playlist/..."}]
```

These mirror the JSON secret schema in [`Documentation/Cloud_Setup.md`](Documentation/Cloud_Setup.md#fill-secrets) — `SPOTIFY_PLAYLISTS` must be a valid JSON array string. Only the variables you actually need have to be set; everything else is skipped.

<br>

On a production server, set `BOT_ENV` as a real environment variable instead of using a `.env` file:

```bash
export BOT_ENV=prod
```

<br>

<h2>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Rocket.svg" width="30px" align="top"/>
    ⠀Run the Bot
</h2>

<h3>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Windows.svg" width="22px" align="top"/>
    ⠀Windows Environment
</h3>

```powershell
.venv\Scripts\activate
python Main.py
```

<h3>
    <img src="https://raw.githubusercontent.com/Dinones/Repository-Images/master/SVG/Linux.svg" width="22px" align="top"/>
    ⠀Linux Environment
</h3>

```bash
source .venv/bin/activate
python3 Main.py
```
