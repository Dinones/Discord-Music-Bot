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
from typing import Dict, Any

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), f"../")))

import Utils.Constants as CONST
import Utils.Colored_Strings as STR
from Utils.Logs import save_exception_to_txt

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'SECRETS'

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
        get_secret_value_response = client.get_secret_value(SecretId = CONST.SECRET_NAME)
    except Exception as error:
        log_path = save_exception_to_txt(error = error, title = 'Retrieve_Secrets')
        print(
            '\n' +
            STR.G_COULD_NOT_GET_AWS_SECRETS.format(
                module   = MODULE_NAME,
                error    = error,
                log_path = log_path
            ) +
            '\n'
        )
        exit()

    return json.loads(get_secret_value_response["SecretString"])

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    print('\n' + json.dumps(get_secrets(), indent=4, ensure_ascii=False, default=str) + '\n')