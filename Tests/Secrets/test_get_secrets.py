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

    def test_get_secrets_falls_back_to_env_and_logs_error_on_exception(self) -> None:

        """
        Test that get_secrets() falls back to _get_secrets_from_env() and logs when AWS raises an exception.
        """

        fake_env_secrets = {"DISCORD_MUSIC_BOT_TOKEN_DEV": "dev-token"}

        with (
            patch("Utils.AWS_Secrets.boto3.session.Session") as mock_session_creator,
            patch("Utils.AWS_Secrets.print") as mock_print,
            patch("Utils.AWS_Secrets.save_exception_to_txt") as mock_save_exception,
            patch("Utils.AWS_Secrets._get_secrets_from_env", return_value = fake_env_secrets) as mock_get_from_env
        ):
            mock_session = mock_session_creator.return_value
            mock_client = mock_session.client.return_value
            mock_client.get_secret_value.side_effect = Exception("aws error")

            result = AWS_Secrets.get_secrets()

        self.assertEqual(
            result,
            fake_env_secrets,
            _color_error_message_in_red(
                f'The "get_secrets()" function should return "{fake_env_secrets}" instead of "{result}" ' +
                'when an error is raised, falling back to _get_secrets_from_env().'
            )
        )

        mock_get_from_env.assert_called_once()

        count = 2
        self.assertEqual(
            mock_print.call_count,
            count,
            _color_error_message_in_red(
                f'Exactly "{count}" logging messages should have been printed in terminal instead of ' +
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

    #######################################################################################################################
    #######################################################################################################################

    def test_get_secrets_returns_empty_dict_and_logs_error_when_env_fallback_also_empty(self) -> None:

        """
        Test that get_secrets() returns an empty dict and logs an error (not just a warning) when both AWS and the
        .env fallback fail to provide any secrets.
        """

        with (
            patch("Utils.AWS_Secrets.boto3.session.Session") as mock_session_creator,
            patch("Utils.AWS_Secrets.print") as mock_print,
            patch("Utils.AWS_Secrets.save_exception_to_txt") as mock_save_exception,
            patch("Utils.AWS_Secrets._get_secrets_from_env", return_value = {}) as mock_get_from_env,
            patch("Utils.AWS_Secrets.STR.SC_COULD_NOT_GET_SECRETS_FROM_AWS_OR_ENV", "both-failed-message")
        ):
            mock_session = mock_session_creator.return_value
            mock_client = mock_session.client.return_value
            mock_client.get_secret_value.side_effect = Exception("aws error")

            result = AWS_Secrets.get_secrets()

        self.assertEqual(
            result,
            {},
            _color_error_message_in_red(
                f'The "get_secrets()" function should return "{{}}" instead of "{result}" when both AWS and the ' +
                '.env fallback fail to provide any secrets.'
            )
        )

        mock_get_from_env.assert_called_once()

        mock_print.assert_any_call("both-failed-message")

        count = 2
        self.assertEqual(
            mock_print.call_count,
            count,
            _color_error_message_in_red(
                f'Exactly "{count}" logging messages should have been printed in terminal instead of ' +
                f'"{mock_print.call_count}".'
            )
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)