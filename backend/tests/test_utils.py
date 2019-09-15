import os
import jwt
import pytest
import sys
import time

sys.path.insert(0, os.getcwd())
import utils

user_id = 1


def test_auth_token_handling(clear_env):
    """
    Tests both auth token encoding and decoding.
    The token should not be expired as by default it lives a few minutes.
    TODO: This is deprecated now that we use Microsoft OAUTH. Review if necessary, or delete.
    """
    pass


def test_auth_token_expiry(clear_env):
    """
    Verifies wether attempting to decode an expired token raises an error.
    The environment values are modified to expire the token in a second.
    TODO: This is deprecated now that we use Microsoft OAUTH. Review if necessary, or delete.
    """
    pass


def test_invalid_auth_token():
    """
    TODO: This is deprecated now that we use Microsoft OAUTH. Review if necessary, or delete.
    """
    pass