###########################################################################################################################
#   Tests for get_secrets() in Utils/AWS_Secrets.                                                                        #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Constants as CONST
import Utils.AWS_Secrets as AWS_Secrets
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Get_Secrets(unittest.TestCase):

    def test_get_secrets_returns_parsed_secret_dictionary(self) -> None:

        """
        Test that get_secrets() returns parsed JSON when AWS call succeeds.
        """

        fake_secret = {
            "DISCORD_TOKEN"  : "abc123",
            "SPOTIFY_SECRET" : "xyz"
        }

        with (
            patch("Utils.AWS_Secrets.boto3.session.Session") as mock_session_creator,
            patch("Utils.AWS_Secrets.print") as mock_print
        ):
            mock_session = mock_session_creator.return_value
            mock_client = mock_session.client.return_value
            mock_client.get_secret_value.return_value = {
                "SecretString": '{"DISCORD_TOKEN":"abc123","SPOTIFY_SECRET":"xyz"}'
            }

            result = AWS_Secrets.get_secrets()

        self.assertEqual(
            result,
            fake_secret,
            _color_error_message_in_red(
                f'The "get_secrets()" function should return "{fake_secret}" instead of "{result}".'
            )
        )

        mock_session.client.assert_called_once_with(
            service_name = "secretsmanager",
            region_name  = CONST.AWS_REGION
        )

        mock_client.get_secret_value.assert_called_once_with(SecretId = CONST.SECRET_NAME)

        count = 1
        self.assertEqual(
            mock_print.call_count,
            count,
            _color_error_message_in_red(
                f'Exactly "{count}" logging message should have been printed in terminal instead of ' +
                f'"{mock_print.call_count}".'
            )
        )

    #######################################################################################################################
    #######################################################################################################################

    def test_get_secrets_returns_none_and_logs_error_on_exception(self) -> None:

        """
        Test that get_secrets() returns None and logs when AWS raises an exception.
        """

        with (
            patch("Utils.AWS_Secrets.boto3.session.Session") as mock_session_creator,
            patch("Utils.AWS_Secrets.print") as mock_print,
            patch("Utils.AWS_Secrets.save_exception_to_txt") as mock_save_exception
        ):
            mock_session = mock_session_creator.return_value
            mock_client = mock_session.client.return_value
            mock_client.get_secret_value.side_effect = Exception("aws error")

            result = AWS_Secrets.get_secrets()

        self.assertIsNone(
            result,
            _color_error_message_in_red(
                f'The "get_secrets()" function should return "None" instead of "{result}" when an error is raised.'
            )
        )

        count = 1
        self.assertEqual(
            mock_print.call_count,
            count,
            _color_error_message_in_red(
                f'Exactly "{count}" logging message should have been printed in terminal instead of ' +
                f'"{mock_print.call_count}".'
            )
        )

        expected_title = "Retrieve_Secrets"
        self.assertEqual(
            mock_save_exception.call_args.kwargs.get("title"),
            expected_title,
            _color_error_message_in_red(
                f'The "save_exception_to_txt()" function should have been called with the "{expected_title}" argument ' +
                f'instead of "{mock_save_exception.call_args.kwargs.get("title")}".'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)