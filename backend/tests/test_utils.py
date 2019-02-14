import os
import jwt
import pytest
import sys
import time
from fixtures import clear_env

sys.path.insert(0, os.getcwd())
import utils

user_id = 1


def test_auth_token_handling(clear_env):
    """
    Tests both auth token encoding and decoding.
    The token should not be expired as by default it lives a few minutes.
    """
    os.environ["SECRET_KEY"] = "potato"

    encoded_token = utils.encode_auth_token(user_id)
    assert encoded_token is not None

    decoded_id = utils.decode_auth_token(encoded_token)
    assert decoded_id == user_id


def test_auth_token_expiry(clear_env):
    """
    Verifies wether attempting to decode an expired token raises an error.
    The environment values are modified to expire the token in a second. 
    """
    utils.token_expiry = 1

    encoded_token = utils.encode_auth_token(user_id)
    
    time.sleep(2)
    assert "Signature expired." in utils.decode_auth_token(encoded_token)

    utils.token_expiry = 180


def test_invalid_auth_token():
    encoded_token = "potatoes_taste_good"
    assert "Invalid token." in utils.decode_auth_token(encoded_token)
