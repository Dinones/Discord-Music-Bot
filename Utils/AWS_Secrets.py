###########################################################################################################################
#                                                                                                                         #
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

###########################################################################################################################
###########################################################################################################################

def get_secrets() -> Dict[str, Any]:

    """
    Retrieve a JSON secret from AWS Secrets Manager and return it as a dictionary.

    Args:
        None

    Returns:
        Dict[str, Any]: Parsed JSON payload stored in the secret's "SecretString".
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
            STR.G_COULD_NOT_GET_AWS_SECRETS.format(
                module   = MODULE_NAME,
                error    = error
            )
        )
        log_path = save_exception_to_txt(error = error, title = 'Retrieve_Secrets')
        return None

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
