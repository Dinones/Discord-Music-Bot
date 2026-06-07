###########################################################################################################################
#   Logging utilities. Saves exceptions to .txt files and configures the Discord logger level.                           #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import re
import time
import logging
import traceback
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Constants as CONST
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
###########################################################################################################################

def set_discord_logging_messages_level(level: str = CONST.LOGGING_LEVEL) -> None:

    """
    Configure discord.py logger output to keep terminal logs clean.

    Args:
        level (str): Discord logging level. If empty, discord loggers are fully disabled. Accepted string
            values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

    Returns:
        None
    """

    logger_names = {"discord"}

    # Include all child loggers such as "discord.http", "discord.gateway", etc.
    for logger_name in logging.root.manager.loggerDict.keys():
        if logger_name == "discord" or logger_name.startswith("discord."):
            logger_names.add(logger_name)

    # Normalize the input before resolving it to a logging constant.
    normalized_level = level.strip().upper()
    resolved_level = None

    if normalized_level:
        candidate_level = getattr(logging, normalized_level, None)
        if isinstance(candidate_level, int):
            resolved_level = candidate_level

    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()

        if resolved_level is None:
            # Empty/invalid level means fully silence discord loggers.
            logger.propagate = False
            logger.disabled = True
            continue

        # Keep discord logs enabled and constrained to the requested level.
        logger.disabled = False
        logger.setLevel(resolved_level)
        logger.propagate = True

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
