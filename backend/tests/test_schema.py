from graphene.test import Client
import os
import jwt
import sys
import time

from queries import query_items, create_item, delete_item, log_in, validate_token
from fixtures import clear_db, clear_env, create_admin_account, create_user_account
sys.path.insert(0, os.getcwd())
from schema import schema, err_auth

client = Client(schema)


def test__show_and_create_items(clear_db):
    """
    Tests possibility to display items
    """
    result = client.execute(query_items)
    assert 'data' in result
    assert 'allItems' in result['data']
    assert 'edges' in result['data']['allItems']
    assert type(result['data']['allItems']['edges']) == list


def test__create_item(clear_db, create_admin_account, create_user_account):
    """
    Tests whether it is possible to create an item
    """
    username, auth_token = "", ""
    item_name = "potato"
    quantity = 1

    # It should be impossible to create an item without being logged in
    result = client.execute(create_item % (item_name, quantity, username, auth_token))
    assert 'errors' in result
    assert err_auth in result['errors'][0]['message']

    # It should be impossible to create an item without being an administrator
    username, password, auth_token = create_user_account
    result = client.execute(create_item % (item_name, quantity, username, auth_token))
    assert 'errors' in result
    assert err_auth in result['errors'][0]['message']

    # It should be possible to create an item as an administrator
    username, password, auth_token = create_admin_account
    result = client.execute(create_item % (item_name, quantity, username, auth_token))
    assert 'errors' not in result
    assert result['data']['createItem']['items'][0]['name'] == item_name


def test__delete_item(clear_db, create_admin_account, create_user_account):
    """
    Tests possibility to delete items
    """
    admin_username, password, admin_auth_token = create_admin_account
    item_name = "potato"
    quantity = 1

    # First, create the item. Previous test validates that this is possible.
    result = client.execute(create_item % (item_name, quantity, admin_username, admin_auth_token))

    # It should be impossible to delete an item without being logged in
    username, auth_token = "", ""
    result = client.execute(delete_item % (item_name, username, auth_token))
    assert 'errors' in result
    assert err_auth in result['errors'][0]['message']

    # It should be impossible to delete an item without being an administrator
    username, password, auth_token = create_user_account
    result = client.execute(delete_item % (item_name, username, auth_token))
    assert 'errors' in result
    assert err_auth in result['errors'][0]['message']

    # It should be possible to delete an item as an administrator
    result = client.execute(delete_item % (item_name, admin_username, admin_auth_token))
    assert 'errors' not in result
    assert len(result['data']['deleteItem']['items']) == 0

    # It should be impossible to delete an item if it doesn't exist
    result = client.execute(delete_item % (item_name, admin_username, admin_auth_token))
    assert 'errors' in result


def test__show_transactions(clear_db, create_admin_account, create_user_account):
    """
    Tests that an authenticated user can view transactions,
    but that a non-authenticated user can not.
    """


def test_check_out_item():
    """
    Tests that a user can correctly check out an item.
    """
    pass


def test_accept_checkout_request():
    """
    Tests that a checkout request can be accepted by an authenticated
    user, but not by a unauthenticated one.
    """
    pass


def test_check_in_item():
    """
    Tests that a user can successfully check back in an item.
    """
    pass


def test_login_user(clear_db, create_user_account, create_admin_account):
    """
    Tests that a user can successfully log in.
    Given that a login also returns a valid token,
    this test also checks whether the validation of tokens works.
    """
    valid_username, valid_password, valid_token = create_user_account
    invalid_username, invalid_password = "", ""

    # It should be impossible to log in with invalid credentials
    result = client.execute(log_in % (invalid_username, invalid_password))
    assert 'errors' in result
    assert result['errors'][0]['message'] == 'Failed to authenticate user.'

    # It should be possible to log in with valid credentials
    result = client.execute(log_in % (valid_username, valid_password))
    assert 'errors' not in result
    assert 'authToken' in result['data']['loginUser']

    # The token returned by the authentication should be valid
    loginData = result['data']['loginUser']
    valid_result = client.execute(validate_token % (valid_username,
                                                    loginData['authToken']))
    assert 'data' in valid_result
    assert valid_result['data']['validateToken']['valid'] == 1



def test__validate_token(clear_db, create_user_account, create_admin_account):
    admin_username, admin_password, admin_auth_token = create_admin_account
    regular_username, regular_password, regular_auth_token = create_user_account
    invalid_username, invalid_token = "", ""

    regular_result = client.execute(validate_token % (regular_username,
                                                      regular_auth_token))
    admin_result = client.execute(validate_token % (admin_username,
                                                    admin_auth_token))
    invalid_result = client.execute(validate_token % (invalid_username,
                                                      invalid_token))
    # We have three levels of validity: 0 (invalid), 1 (regular), 2 (admin).
    assert invalid_result['data']['validateToken']['valid'] == 0
    assert regular_result['data']['validateToken']['valid'] == 1
    assert admin_result['data']['validateToken']['valid'] == 2
