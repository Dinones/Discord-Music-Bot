###########################################################################################################################
#   Downloads private command files from an S3 bucket into Commands/Extra_Commands/ at bot startup.                      #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

import os
import sys
import boto3
from typing import List

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), f"../")))

import Utils.Constants as CONST
import Utils.Colored_Strings as STR
from Utils.Logs import save_exception_to_txt

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'S3'
EXTRA_COMMANDS_ABS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "Commands", "Extra_Commands")
)

###########################################################################################################################
###########################################################################################################################

def download_extra_commands(bucket: str) -> bool:

    """
    Download all .py files from the S3 extra-commands prefix into Commands/Extra_Commands/.
    Skips silently when bucket is empty so the feature is opt-in.

    Args:
        bucket (str): S3 bucket name read from AWS Secrets Manager at startup.

    Returns:
        bool: True if the download succeeded (or was skipped), False on error.
    """

    if not bucket:
        print(STR.SC_EXTRA_COMMANDS_SKIP)
        return True

    try:
        session = boto3.session.Session()
        client = session.client(
            service_name = 's3',
            region_name  = CONST.AWS_REGION
        )

        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(
            Bucket = bucket,
            Prefix = CONST.S3_EXTRA_COMMANDS_PREFIX
        )

        py_keys: List[str] = []
        for page in pages:
            for obj in page.get('Contents', []):
                key = obj['Key']
                if key.endswith('.py'):
                    py_keys.append(key)

        if not py_keys:
            print(STR.SC_EXTRA_COMMANDS_NONE_FOUND.format(prefix = CONST.S3_EXTRA_COMMANDS_PREFIX))
            return True

        os.makedirs(EXTRA_COMMANDS_ABS_PATH, exist_ok = True)

        for key in py_keys:
            filename = os.path.basename(key)
            dest = os.path.join(EXTRA_COMMANDS_ABS_PATH, filename)
            client.download_file(bucket, key, dest)

        print(STR.SC_EXTRA_COMMANDS_DOWNLOADED.format(count = len(py_keys)))
        return True

    except Exception as error:
        print(STR.SC_EXTRA_COMMANDS_ERROR.format(error = error))
        save_exception_to_txt(error = error, title = 'Download_Extra_Commands')
        return False

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    download_extra_commands("")
