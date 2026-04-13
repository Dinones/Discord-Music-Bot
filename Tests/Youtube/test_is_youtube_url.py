###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import Utils.Youtube
from Tests.Helpers.helpers import _color_error_message_in_red

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

class Test_Is_Youtube_URL(unittest.TestCase):

    def test_is_youtube_url_accepts_supported_youtube_domains(self) -> None:

        """
        Test that _is_youtube_url() accepts supported YouTube domains and subdomains.
        """

        for url in (
            "https://www.youtube.com/watch?v=abc123",
            "https://youtube.com/watch?v=abc123",
            "https://m.youtube.com/watch?v=abc123",
            "https://music.youtube.com/watch?v=abc123",
            "https://youtu.be/abc123"
        ):
            self.assertTrue(
                Utils.Youtube._is_youtube_url(url),
                _color_error_message_in_red(f'The valid "{url}" URL has been flagged as invalid.')
            )

    #######################################################################################################################
    #######################################################################################################################

    def test_is_youtube_url_rejects_invalid_domains_or_schemes(self) -> None:

        """
        Test that _is_youtube_url() rejects non-YouTube domains and invalid schemes.
        """

        for url in (
            "https://example.com/watch?v=abc123",
            "https://youtube.fake/watch?v=abc123",
            "ftp://youtube.com/watch?v=abc123",
            "not a url",
            ""
        ):
            self.assertFalse(
                Utils.Youtube._is_youtube_url(url),
                _color_error_message_in_red(f'The invalid "{url}" URL was flagged as valid.')
            )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    unittest.main(buffer = True)