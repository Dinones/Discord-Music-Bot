###########################################################################################################################
#   Interactive debug menu for testing AWS Secrets Manager and YouTube cookie retrieval.                                  #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
from time import time
from unittest.mock import Mock, AsyncMock

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils.AWS_Secrets import *

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Secrets'

###########################################################################################################################
###########################################################################################################################

# 1. Retrieve bot secrets from AWS
# 2. Retrieve Youtube cookies from AWS
def _retrieve_secrets(option):

    secret_names = {
        '1': 'bot secrets',
        '2': 'Youtube cookies'
    }

    print(
        STR.M_SELECTED_OPTION.format(
            module = MODULE_NAME,
            option = option,
            action = f"Retrieving {secret_names.get(option, '')} from AWS",
            path   = ''
        )
    )

    if option == '1':
        secrets = get_secrets()
    elif option == '2':
        secrets = get_youtube_cookies()

    if secrets:
        response = input(STR.SC_ASK_TO_PRINT_SECRETS).strip().lower()
        if response in ('', 'y', 'yes'):
            print('\n', json.dumps(secrets, indent=4, ensure_ascii=False, default=str))


###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

def main_menu():
        print('\n' + STR.M_MENU.format(module = MODULE_NAME))
        print(STR.M_MENU_OPTION.format(index = 1, option = 'Retrieve bot secrets from AWS'))
        print(STR.M_MENU_OPTION.format(index = 2, option = 'Retrieve Youtube cookies from AWS'))

        option = input('\n' + STR.M_OPTION_SELECTION.format(module = MODULE_NAME))

        menu_options = {
            '1': _retrieve_secrets,
            '2': _retrieve_secrets,
        }

        if option in menu_options:
            print()
            menu_options[option](option)
            print()
        else:
            print('\n' + STR.M_INVALID_OPTION.format(module = MODULE_NAME) + '\n')

###########################################################################################################################
###########################################################################################################################

if __name__ == "__main__":
    main_menu()