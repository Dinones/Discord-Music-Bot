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