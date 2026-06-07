###########################################################################################################################
#   Tests for save_exception_to_txt() in Utils/Logs.                                                                     #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from tempfile import TemporaryDirectory

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Logs

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class TestSaveExceptionToTxt(unittest.TestCase):

    def test_creates_file_and_writes_traceback_and_returns_uri(self) -> None:

        with TemporaryDirectory() as tmpdir:
            fixed_timestamp = 1234567890

            try:
                1 / 0
            except Exception as error:
                with (
                    patch.object(Utils.Logs, "OUTPUT_DIR", tmpdir),
                    patch.object(Utils.Logs.time, "time", return_value = fixed_timestamp)
                ):
                    uri = Utils.Logs.save_exception_to_txt(error, "division by zero")

            self.assertTrue(uri.startswith("file:///"))

            expected_path = Path(tmpdir) / f"division_by_zero_{fixed_timestamp}.txt"
            self.assertTrue(expected_path.exists())

            content = expected_path.read_text(encoding="utf-8")
            self.assertIn("Traceback (most recent call last)", content)

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
