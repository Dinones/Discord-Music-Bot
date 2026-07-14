## 📋ㅤTable of Contents

- [🤖ㅤCreate the Discord Application](#create-app)
- [⚙️ㅤConfigure the Bot User](#configure-bot)
- [🔑ㅤSave the Bot Token](#save-token)
- [🛡️ㅤConfigure Install Permissions](#install-permissions)
- [🔗ㅤInstall the Bot in Your Server](#install-server)
- [✅ㅤVerify the Setup](#verify)
- [🧯ㅤTroubleshooting](#troubleshooting)

<br><br>

# 🤖ㅤDiscord Bot Setup

> [!IMPORTANT]
> You need a Discord account with `Manage Server` permission in the target server. Without that permission, Discord will not let you add the bot to the server.

<br>

<a id="create-app"></a>

## 🤖ㅤCreate the Discord Application

1. Open the <a href="https://discord.com/developers/applications">Discord Developer Portal</a>.

2. Click `New Application`.

3. Set the application name, for example:

   ```text
   Discord Music Bot
   ```

4. Accept the Discord Developer Terms if prompted.

5. Click `Create`.

6. Open `General Information`.

7. Optionally set:

   - `App Icon`
   - `Description`
   - `Tags`

8. Copy the `Application ID` and keep it available if you need to build a manual OAuth invite URL later.

<br>

<a id="configure-bot"></a>

## ⚙️ㅤConfigure the Bot User

1. In the application sidebar, open `Bot`.

2. If Discord shows an `Add Bot` button, click it to create the bot user.

3. Under `Token`, click `Reset Token`.

4. Copy the token immediately.

> [!CAUTION]
> The bot token is equivalent to a password. Do **NOT** commit it, send it in chat, or paste it into screenshots. If the token is ever exposed, reset it immediately in the Discord Developer Portal. The old token stops working as soon as Discord generates the new one.
>
> Prefer storing it in AWS Secrets Manager (see [`Cloud_Setup.md`](Cloud_Setup.md)). If you don't have AWS access, the bot falls back to reading it from the gitignored `.env` file. Treat that file with the same care as the token itself (never share it, screenshot it, or move it outside this machine).

5. Under `Authorization Flow`, disable:

   - `Requires OAuth2 Code Grant`

6. Under `Privileged Gateway Intents`, enable:

   - `Presence Intent`
   - `Server Members Intent`
   - `Message Content Intent`

> [!NOTE]
> This project currently creates the bot with `discord.Intents.all()`. That means Discord expects the privileged intents above to be enabled. `Message Content Intent` is required for prefix commands such as `!play`, `!queue`, and `!pause`.

7. Under `Public Bot`, choose the safest option for your use case:

   - Disable it if only you should be able to install the bot.
   - Enable it only if other Discord users should be able to add the bot to their servers.

8. Click `Save Changes`.

<br>

<a id="install-permissions"></a>

## 🛡️ㅤConfigure Install Permissions

The bot needs Discord permissions to read commands, send responses, react to messages, join voice channels, and play audio.

1. In the Discord Developer Portal, open your application.
2. Open `Installation`.
3. Under `Installation Contexts`, enable:

   - `Guild Install`

4. Under `Install Link`, select:

   - `Discord Provided Link`

5. Under `Default Install Settings`, configure `Guild Install`:

   - `Scopes`: `bot`
   - `Scopes`: `applications.commands`

6. In `Bot Permissions`, select:

   - `View Channels`
   - `Send Messages`
   - `Embed Links`
   - `Attach Files`
   - `Read Message History`
   - `Add Reactions`
   - `Connect`
   - `Speak`
   - `Use Voice Activity`

> [!NOTE]
> `applications.commands` is safe to include even though this project currently uses prefix commands. It keeps the install settings ready if slash commands are added later.

> [!CAUTION]
> Avoid using `Administrator` unless this is a private trusted server. The permissions above are enough for the bot features in this project.

7. Click `Save Changes`.

<br>

<a id="install-server"></a>

## 🔗ㅤInstall the Bot in Your Server

1. In the Discord Developer Portal, open your application.

2. Open `Installation`.

3. Copy the `Install Link`.

4. Paste the link into your browser.

5. Choose `Add to server`.

6. Select your Discord server.

7. Review the requested permissions.

8. Click `Authorize`.

9. Complete the captcha if Discord asks for one.

After authorization, the bot should appear in your server member list. It may appear offline until you run `Main.py`.
