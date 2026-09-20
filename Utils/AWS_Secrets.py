###########################################################################################################################
#   Retrieves bot secrets and YouTube cookies from AWS Secrets Manager.                                                   #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

import os
import sys
import json
import boto3
from pathlib import Path
from typing import Dict, Any, Optional

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), f"../")))

import Utils.Constants as CONST
import Utils.Colored_Strings as STR
from Utils.Logs import save_exception_to_txt

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Secrets'
COOKIES_ABS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", CONST.YT_COOKIES_FILE_PATH))

# Keys of the AWS secret JSON payload (see Documentation/Cloud_Setup.md) that can also be sourced from
# plain environment variables / the .env file when AWS Secrets Manager is unreachable.
_ENV_FALLBACK_STRING_KEYS = (
    "DISCORD_MUSIC_BOT_TOKEN_PROD",
    "DISCORD_MUSIC_BOT_TOKEN_DEV",
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
    "BOT_ACTIVITY_NAME",
    "DISCORD_SERVER_NAME",
    "DISCORD_TEXT_CHANNEL_PROD",
    "DISCORD_TEXT_CHANNEL_DEV",
    "S3_EXTRA_COMMANDS_BUCKET",
)

###########################################################################################################################
###########################################################################################################################

def _get_secrets_from_env() -> Dict[str, Any]:

    """
    Build a secrets dictionary from environment variables (populated by python-dotenv from .env). Used as a fallback
    when AWS Secrets Manager cannot be reached, e.g. in environments without AWS access. Mirrors the JSON secret
    schema documented in Documentation/Cloud_Setup.md; "SPOTIFY_PLAYLISTS" is read as a JSON array string.

    Args:
        None

    Returns:
        Dict[str, Any]: Secrets dictionary built from whichever of the expected keys are set, empty if none are set.
    """

    secrets = {}
    for key in _ENV_FALLBACK_STRING_KEYS:
        value = os.environ.get(key, "").strip()
        if value:
            secrets[key] = value

    playlists_raw = os.environ.get("SPOTIFY_PLAYLISTS", "").strip()
    if playlists_raw:
        try:
            secrets["SPOTIFY_PLAYLISTS"] = json.loads(playlists_raw)
        except json.JSONDecodeError as error:
            print(
                STR.G_ACTION_NOT_DONE.format(
                    user   = MODULE_NAME,
                    action = 'parse SPOTIFY_PLAYLISTS from .env',
                    reason = error
                )
            )
            save_exception_to_txt(error = error, title = 'Parse_Env_Playlists')

    return secrets

###########################################################################################################################
###########################################################################################################################

def get_secrets() -> Dict[str, Any]:

    """
    Retrieve a JSON secret from AWS Secrets Manager and return it as a dictionary. Falls back to environment
    variables (.env) when AWS Secrets Manager is unreachable; only logs an error (instead of a warning) if
    that fallback also yields no usable secrets.

    Args:
        None

    Returns:
        Dict[str, Any]: Parsed JSON payload stored in the secret's "SecretString", or a dictionary built from
            environment variables if AWS Secrets Manager could not be reached. Empty if neither source has
            any secrets.
    """

    # Create the Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name = 'secretsmanager',
        region_name  = CONST.AWS_REGION
    )

    try:
        secret_value_response = client.get_secret_value(SecretId = CONST.SECRET_NAME)

    except Exception as error:
        print(
            STR.SC_COULD_NOT_GET_AWS_SECRETS.format(
                error = error
            )
        )
        log_path = save_exception_to_txt(error = error, title = 'Retrieve_Secrets')

        env_secrets = _get_secrets_from_env()
        if not env_secrets:
            print(STR.SC_COULD_NOT_GET_SECRETS_FROM_AWS_OR_ENV)
            return {}

        print(STR.SC_FALLING_BACK_TO_ENV_SECRETS)
        return env_secrets

    print(STR.SC_RETRIEVED_SECRETS_FROM_AWS)

    return json.loads(secret_value_response["SecretString"])

###########################################################################################################################
###########################################################################################################################

def get_youtube_cookies() -> Optional[str]:

    """
    Retrieve YouTube cookies from AWS Secrets Manager and save them in the local cookies file path.

    Args:
        None

    Returns:
        Optional[str]: Absolute URI to the saved cookies file, or None if retrieval fails.
    """

    # Create the Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name = 'secretsmanager',
        region_name  = CONST.AWS_REGION
    )

    try:
        secret_value_response = client.get_secret_value(SecretId = CONST.YT_COOKIES_SECRET_NAME)

    except Exception as error:
        print(
            STR.SC_COULD_NOT_GET_YT_COOKIES.format(
                error = error
            )
        )
        log_path = save_exception_to_txt(error = error, title = 'Retrieve_Youtube_Cookies')

        return None

    cookies_content = secret_value_response.get("SecretString", "").strip()

    # Retrieved AWS cookies file is empty
    if not cookies_content or cookies_content == "{}":
        print(STR.SC_YT_COOKIES_EMPTY)
        return None

    # The newline parameter remove duplicated line breaks
    with open(COOKIES_ABS_PATH, 'w+', encoding = 'utf-8', newline='\n') as file:
        file.write(cookies_content)

    cookies_path = Path(COOKIES_ABS_PATH).resolve().as_uri()

    print(
        STR.SC_RETRIEVED_YT_COOKIES_FROM_AWS.format(
            path = cookies_path
        )
    )

    return cookies_path

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    import Debug.AWS_Secrets_Debug

    Debug.AWS_Secrets_Debug.main_menu()
