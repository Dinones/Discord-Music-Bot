###########################################################################################################################
#   Tests for download_extra_commands() in Utils/AWS_S3.                                                                  #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch, call

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Constants as CONST
import Utils.AWS_S3 as AWS_S3
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

FAKE_BUCKET = "discord-music-bot-test"

###########################################################################################################################
###########################################################################################################################

class Test_Download_Extra_Commands(unittest.TestCase):

    def _make_paginator(self, mock_client, pages):
        mock_paginator = mock_client.get_paginator.return_value
        mock_paginator.paginate.return_value = pages
        return mock_paginator

    #######################################################################################################################
    #######################################################################################################################

    def test_empty_bucket_skips_and_returns_true(self) -> None:

        """
        Test that download_extra_commands("") skips all S3 calls and returns True.
        """

        with (
            patch("Utils.AWS_S3.boto3.session.Session") as mock_session_creator,
            patch("Utils.AWS_S3.print") as mock_print
        ):
            result = AWS_S3.download_extra_commands("")

        self.assertTrue(
            result,
            _color_error_message_in_red(
                'download_extra_commands("") should return True when bucket is empty.'
            )
        )

        mock_session_creator.assert_not_called()

        count = 1
        self.assertEqual(
            mock_print.call_count,
            count,
            _color_error_message_in_red(
                f'Exactly "{count}" logging message should have been printed instead of '
                f'"{mock_print.call_count}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_downloads_py_files_and_returns_true(self) -> None:

        """
        Test that .py files are listed and downloaded, and True is returned on success.
        """

        pages = [
            {
                'Contents': [
                    {'Key': 'extra-commands/command_a.py'},
                    {'Key': 'extra-commands/command_b.py'},
                ]
            }
        ]

        with (
            patch("Utils.AWS_S3.boto3.session.Session") as mock_session_creator,
            patch("Utils.AWS_S3.os.makedirs"),
            patch("Utils.AWS_S3.print") as mock_print
        ):
            mock_session = mock_session_creator.return_value
            mock_client = mock_session.client.return_value
            self._make_paginator(mock_client, pages)

            result = AWS_S3.download_extra_commands(FAKE_BUCKET)

        self.assertTrue(
            result,
            _color_error_message_in_red(
                'download_extra_commands() should return True when files are downloaded successfully.'
            )
        )

        mock_session.client.assert_called_once_with(
            service_name = 's3',
            region_name  = CONST.AWS_REGION
        )

        mock_client.get_paginator.assert_called_once_with('list_objects_v2')
        mock_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket = FAKE_BUCKET,
            Prefix = CONST.S3_EXTRA_COMMANDS_PREFIX
        )

        expected_downloads = [
            call(FAKE_BUCKET, 'extra-commands/command_a.py',
                 os.path.join(AWS_S3.EXTRA_COMMANDS_ABS_PATH, 'command_a.py')),
            call(FAKE_BUCKET, 'extra-commands/command_b.py',
                 os.path.join(AWS_S3.EXTRA_COMMANDS_ABS_PATH, 'command_b.py')),
        ]
        self.assertEqual(
            mock_client.download_file.call_args_list,
            expected_downloads,
            _color_error_message_in_red(
                f'download_file() should have been called with {expected_downloads} instead of '
                f'{mock_client.download_file.call_args_list}.'
            )
        )

        count = 1
        self.assertEqual(
            mock_print.call_count,
            count,
            _color_error_message_in_red(
                f'Exactly "{count}" logging message should have been printed instead of '
                f'"{mock_print.call_count}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_non_py_files_are_ignored(self) -> None:

        """
        Test that non-.py files in the S3 prefix are not downloaded.
        """

        pages = [
            {
                'Contents': [
                    {'Key': 'extra-commands/command_a.py'},
                    {'Key': 'extra-commands/README.md'},
                    {'Key': 'extra-commands/'},
                ]
            }
        ]

        with (
            patch("Utils.AWS_S3.boto3.session.Session") as mock_session_creator,
            patch("Utils.AWS_S3.os.makedirs"),
            patch("Utils.AWS_S3.print")
        ):
            mock_session = mock_session_creator.return_value
            mock_client = mock_session.client.return_value
            self._make_paginator(mock_client, pages)

            AWS_S3.download_extra_commands(FAKE_BUCKET)

        count = 1
        self.assertEqual(
            mock_client.download_file.call_count,
            count,
            _color_error_message_in_red(
                f'Only "{count}" download_file() call should have been made (only .py files) instead of '
                f'"{mock_client.download_file.call_count}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_no_files_found_returns_true(self) -> None:

        """
        Test that an empty S3 prefix returns True without calling download_file.
        """

        pages = [{}]

        with (
            patch("Utils.AWS_S3.boto3.session.Session") as mock_session_creator,
            patch("Utils.AWS_S3.print") as mock_print
        ):
            mock_session = mock_session_creator.return_value
            mock_client = mock_session.client.return_value
            self._make_paginator(mock_client, pages)

            result = AWS_S3.download_extra_commands(FAKE_BUCKET)

        self.assertTrue(
            result,
            _color_error_message_in_red(
                'download_extra_commands() should return True when no files are found in S3.'
            )
        )

        mock_client.download_file.assert_not_called()

        count = 1
        self.assertEqual(
            mock_print.call_count,
            count,
            _color_error_message_in_red(
                f'Exactly "{count}" logging message should have been printed instead of '
                f'"{mock_print.call_count}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_exception_returns_false_and_logs_error(self) -> None:

        """
        Test that an S3 exception returns False and logs via save_exception_to_txt.
        """

        with (
            patch("Utils.AWS_S3.boto3.session.Session") as mock_session_creator,
            patch("Utils.AWS_S3.print") as mock_print,
            patch("Utils.AWS_S3.save_exception_to_txt") as mock_save_exception
        ):
            mock_session = mock_session_creator.return_value
            mock_client = mock_session.client.return_value
            mock_client.get_paginator.side_effect = Exception("s3 error")

            result = AWS_S3.download_extra_commands(FAKE_BUCKET)

        self.assertFalse(
            result,
            _color_error_message_in_red(
                'download_extra_commands() should return False when an exception is raised.'
            )
        )

        count = 1
        self.assertEqual(
            mock_print.call_count,
            count,
            _color_error_message_in_red(
                f'Exactly "{count}" logging message should have been printed instead of '
                f'"{mock_print.call_count}".'
            )
        )

        expected_title = "Download_Extra_Commands"
        self.assertEqual(
            mock_save_exception.call_args.kwargs.get("title"),
            expected_title,
            _color_error_message_in_red(
                f'save_exception_to_txt() should have been called with title="{expected_title}" instead of '
                f'"{mock_save_exception.call_args.kwargs.get("title")}".'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)
