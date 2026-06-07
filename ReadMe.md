## 🐍ㅤPython Setup

This project requires **Python 3.12**.

### 🪟ㅤWindows Environment

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r Requirements.txt
```

### 🐧ㅤLinux Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r Requirements.txt
```

<br>

## 🎞️ㅤFFmpeg Installation

This bot requires `ffmpeg` to play audio.

### 🪟ㅤWindows Environment

Run a powershell as administrator and run:

```powershell
choco install ffmpeg -y
```

### 🐧ㅤLinux Environment

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

<br>

## ☁️ㅤAWS Setup

The bot reads its secrets (Discord token, Spotify credentials, etc.) from AWS Secrets Manager. Follow the steps in [`Documentation/Cloud_Setup.md`](Documentation/Cloud_Setup.md) to provision the required AWS resources and fill the secret values.

<br>

## ⚙️ㅤEnvironment Configuration

Create a `.env` file in the project root to configure local settings. This file is gitignored and never committed.

```env
BOT_ENV=dev
```

| Variable  | Values          | Default | Description                                       |
|-----------|-----------------|---------|---------------------------------------------------|
| `BOT_ENV` | `dev` \| `prod` | `dev`   | Selects which Discord token and channel to use.   |

<br>

On a production server, set `BOT_ENV` as a real environment variable instead of using a `.env` file:

```bash
export BOT_ENV=prod
```

<br>

## 🚀ㅤRun the Bot

### 🪟ㅤWindows Environment

```powershell
.venv\Scripts\activate
python Main.py
```

### 🐧ㅤLinux Environment

```bash
source .venv/bin/activate
python3 Main.py
```
