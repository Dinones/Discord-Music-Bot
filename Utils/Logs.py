###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import re
import time
import traceback
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Logs'))

###########################################################################################################################
###########################################################################################################################

def save_exception_to_txt(error: BaseException, title: str) -> str:

    """
    Save the full exception traceback into a .txt file.

    Args:
        error (BaseException): The exception instance caught in an except block.
        title (str): A human-readable title to use in the filename.

    Returns:
        str: Absolute path to the created .txt file.
    """

    safe_title = re.sub(r"[^a-zA-Z0-9._-]+", "_", title).strip("_") or "error"

    output_path = os.path.join(OUTPUT_DIR, f"{safe_title}_{int(time.time())}.txt")

    # Full traceback similar to what you'd see when raising the error
    content = "".join(traceback.format_exception(type(error), error, error.__traceback__))

    with open(output_path, 'w+') as log:
        log.write(content)

    path = Path(output_path).resolve().as_uri()

    print(STR.LOG_CREATED.format(log_path = path))

    return path

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass