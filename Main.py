###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import discord
import inspect
import pkgutil
import Commands
import importlib
from typing import Dict, Any
from dotenv import load_dotenv
from discord.ext import commands
from dataclasses import dataclass

from Utils import Constants as CONST
from Utils import Colored_Strings as STR
from Utils.AWS_Secrets import get_secrets
from Utils.Logs import save_exception_to_txt, set_discord_logging_messages_level

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = "Main"
VALID_ENVIRONMENTS = ('prod', 'dev')

###########################################################################################################################
###########################################################################################################################

@dataclass(frozen = True)
class Bot_Runtime_Config:

    """
    Runtime configuration loaded from non-versioned sources (env vars / AWS Secrets).
    """

    env                  : str
    discord_server_name  : str
    activity             : discord.Activity | None
    discord_text_channel : int | None

###########################################################################################################################
###########################################################################################################################

def _resolve_environment() -> str:

    """
    Read the active environment from the BOT_ENV environment variable.

    Args:
        None

    Returns:
        str: 'prod' or 'dev'. Defaults to 'dev' if BOT_ENV is unset or invalid.
    """

    env_raw = os.environ.get('BOT_ENV', 'dev').strip().lower()
    env = env_raw if env_raw in VALID_ENVIRONMENTS else 'dev'

    if env != env_raw:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = MODULE_NAME,
                action = 'read BOT_ENV',
                reason = f'Unknown environment "{env_raw}", defaulting to "dev"'
            )
        )

    return env

###########################################################################################################################
###########################################################################################################################

def _get_discord_token(secrets: Dict[str, Any], env: str) -> str:

    """
    Retrieve the Discord bot token for the active environment from AWS Secrets.

    Args:
        secrets (Dict[str, Any]) : Parsed secret dictionary.
        env (str) : Active environment ('prod' or 'dev').

    Returns:
        str: The Discord token if available, otherwise an empty string.
    """

    token_key = f'DISCORD_MUSIC_BOT_TOKEN_{env.upper()}'
    return secrets.get(token_key, '').strip()

###########################################################################################################################
###########################################################################################################################

def _resolve_activity_type(activity_type: str = CONST.BOT_ACTIVITY_TYPE) -> discord.ActivityType:

    """
    Resolve string activity type into Discord's ActivityType enum.

    Args:
        activity_type (str): Text activity type.

    Returns:
        discord.ActivityType: Parsed activity type.
    """

    normalized_type = activity_type.lower().strip()

    mapping = {
        "playing"   : discord.ActivityType.playing,
        "watching"  : discord.ActivityType.watching,
        "streaming" : discord.ActivityType.streaming,
        "listening" : discord.ActivityType.listening,
        "competing" : discord.ActivityType.competing,
    }

    return mapping.get(normalized_type, discord.ActivityType.listening)

###########################################################################################################################
###########################################################################################################################

def _build_runtime_config(secrets: Dict[str, Any], env: str) -> Bot_Runtime_Config:

    """
    Build runtime Discord settings from environment variables and AWS Secrets.

    Args:
        secrets (Dict[str, Any]): Parsed secret dictionary.
        env     (str): Active environment ('prod' or 'dev').

    Returns:
        Bot_Runtime_Config: Runtime config object.
    """

    activity_type       = CONST.BOT_ACTIVITY_TYPE
    activity_name       = secrets.get('BOT_ACTIVITY_NAME', '')
    discord_server_name = secrets.get('DISCORD_SERVER_NAME', '')

    activity = None
    if activity_name:
        activity = discord.Activity(type = _resolve_activity_type(activity_type), name = activity_name)

    channel_str = secrets.get(f'DISCORD_TEXT_CHANNEL_{env.upper()}', '').strip()
    discord_text_channel = int(channel_str) if channel_str.isdigit() else None

    return Bot_Runtime_Config(
        env                  = env,
        discord_server_name  = discord_server_name,
        activity             = activity,
        discord_text_channel = discord_text_channel
    )

###########################################################################################################################
###########################################################################################################################

def _register_all_commands(bot: commands.Bot) -> None:

    """
    Dynamically discover and register every command module under the "Commands" package. This loader imports each python
    module from the Commands folder and executes every function following the naming convention "register_*_command(bot)".

    Args:
        bot (commands.Bot): Bot instance where commands should be registered.

    Returns:
        None
    """

    module_infos = [
        module_info for module_info in pkgutil.iter_modules(Commands.__path__) if (
            not module_info.ispkg and
            not module_info.name.startswith("_")
        )
    ]

    # Sort modules by name to keep command registration order deterministic across environments
    module_infos.sort(key = lambda module_info: module_info.name.lower())

    for module_info in module_infos:

        module = importlib.import_module(f"Commands.{module_info.name}")

        register_functions = [
            member for _, member in inspect.getmembers(module, inspect.isfunction) if (
                member.__name__.startswith("register_") and
                member.__name__.endswith("_command")
            )
        ]

        for register_function in register_functions:
            register_function(bot)

###########################################################################################################################
###########################################################################################################################

def _build_bot(runtime_config: Bot_Runtime_Config) -> commands.Bot:

    """
    Build and configure the Discord bot instance with the required intents and events.

    Returns:
        commands.Bot: Configured Discord bot client.
    """

    intents = discord.Intents.all()

    bot = commands.Bot(
        command_prefix   = CONST.BOT_PREFIX,
        intents          = intents,
        activity         = runtime_config.activity,
        case_insensitive = True # Insensitive command prefixes
    )

    # Load command handlers from every Commands/*.py module using the registration naming convention.
    _register_all_commands(bot)

    #######################################################################################################################
    #######################################################################################################################

    @bot.event
    async def on_ready() -> None:
        print(STR.G_BOT_INITIALIZED)

        if bot.user is None:
            return None

        print(
            STR.G_BOT_CONNECTED_AS.format(
                bot_user = bot.user,
                bot_id   = bot.user.id
            )
        )
        print(STR.G_BOT_ENVIRONMENT.format(environment = runtime_config.env))

        if runtime_config.discord_text_channel:
            try:
                channel = await bot.fetch_channel(runtime_config.discord_text_channel)
                await channel.send(MSG.BOT_STARTED)
            except Exception as error:
                save_exception_to_txt(error = error, title = 'Bot_Startup_Message')
                print(
                    STR.G_ACTION_NOT_DONE.format(
                        user   = MODULE_NAME,
                        action = 'send startup message to notification channel',
                        reason = error
                    )
                )

    #######################################################################################################################
    #######################################################################################################################

    @bot.event
    async def on_message(message: discord.Message) -> None:

        if message.author.bot:
            return None

        if message.guild is None:
            return None

        if runtime_config.discord_server_name:
            if message.guild.name.lower() != runtime_config.discord_server_name.lower():
                return None

        if not message.content.startswith(CONST.BOT_PREFIX):
            return None

        await bot.process_commands(message)

    #######################################################################################################################
    #######################################################################################################################

    @bot.event
    async def on_command_error(context: commands.Context, error: commands.CommandError) -> None:

        if isinstance(error, commands.CommandNotFound):
            command_text = context.message.content.strip()

            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = context.author.name.capitalize(),
                    action = 'use an unknown command',
                    reason = f'"{command_text}"'
                )
            )

            await context.send(
                MSG.UNKNOWN_COMMAND.format(
                    command = command_text
                )
            )
            return

        raise error

    #######################################################################################################################
    #######################################################################################################################

    return bot

###########################################################################################################################
###########################################################################################################################

def main() -> None:

    """
    Startup entrypoint for the Discord music bot.
    """

    set_discord_logging_messages_level()

    load_dotenv()
    env = _resolve_environment()

    # Retrieve Discord and Spotify secrets from AWS
    secrets = get_secrets()
    if not isinstance(secrets, dict):
        secrets = {}

    # Craft the Discord token for the active environment
    token = _get_discord_token(secrets, env)
    if not token:
        print(STR.G_COULD_NOT_INITIALIZE_BOT.format(reason = f'Missing Discord token for "{env}" environment'))
        return

    # Configure and build the bot
    runtime_config = _build_runtime_config(secrets, env)
    bot = _build_bot(runtime_config)

    # Run the bot
    try:
        bot.run(token)
    except Exception as error:
        print(STR.G_COULD_NOT_INITIALIZE_BOT.format(reason = error))
        save_exception_to_txt(error = error, title = "Bot_Startup")

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    print()
    main()
    print()
