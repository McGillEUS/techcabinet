from graphene.test import Client
import os
import jwt
import sys
import time

from queries import query_items, create_item, delete_item, log_in, validate_token, checkout_item_loggedin, checkout_item
sys.path.insert(0, os.getcwd())
from schema import schema, err_auth

client = Client(schema)
item_name = "potato"

def test_inventory__show_and_create_items(clear_db):
    """
    Tests possibility to display items
    """
    result = client.execute(query_items)
    assert 'data' in result
    assert 'allItems' in result['data']
    assert 'edges' in result['data']['allItems']
    assert type(result['data']['allItems']['edges']) == list


def test_inventory__create_item(clear_db, create_admin_account, create_user_account):
    """
    Tests whether it is possible to create an item
    """
    username, auth_token = "", ""
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


def test_inventory__delete_item(clear_db, create_admin_account, create_user_account):
    """
    Tests possibility to delete items
    """
    admin_username, password, admin_auth_token = create_admin_account
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


def test_transactions__checkout_item(clear_db, create_admin_account, create_user_account):
    """
    Tests that an authenticated user can create transactions by checking
    out an item, but that a non-authenticated user can not.

    This test is linked with the next four tests.
    """
    admin_username, admin_password, admin_auth_token = create_admin_account
    reg_username, reg_password, reg_auth_token = create_user_account

    # We want to share the credentials across the linked tests,
    # We don't want to re-run "create_admin_account" if we don't clear the DB.
    os.environ['admin_username'] = admin_username
    os.environ['admin_password'] = admin_password
    os.environ['admin_auth_token'] = admin_auth_token
    os.environ['reg_username'] = reg_username
    os.environ['reg_password'] = reg_password
    os.environ['reg_auth_token'] = reg_auth_token

    invalid_username, invalid_auth_token = "", ""

    quantity = 3

    # First, create the item.
    result = client.execute(create_item % (item_name, quantity, admin_username, admin_auth_token))

    quantity = 1
    # Next, attempt to check out the item as a user with invalid credentials
    invalid_username_result = client.execute(checkout_item_loggedin % (invalid_username, item_name,
                                                                       quantity, reg_auth_token))
    invalid_token_result = client.execute(checkout_item_loggedin % (reg_username, item_name,
                                                                    quantity, invalid_auth_token))
    assert 'errors' in invalid_username_result
    assert 'errors' in invalid_token_result
    assert 'You do not have an account' in invalid_username_result['errors'][0]['message']

    # Now attempt to check out the item as a user with valid credentials
    regular_user_result = client.execute(checkout_item_loggedin % (reg_username, item_name,
                                                                   quantity, reg_auth_token))
    admin_user_result = client.execute(checkout_item_loggedin % (admin_username, item_name,
                                                                 quantity, admin_auth_token))
    assert 'data' in regular_user_result
    assert 'data' in admin_user_result
    assert regular_user_result['data']['checkOutItem']['items'][0]['name'] == item_name
    assert admin_user_result['data']['checkOutItem']['items'][0]['name'] == item_name


def test_transactions__checkout_item_create_user():
    """
    Tests the possibility of creating accounts as part of the checkout flow.
    """
    username = "poutine"
    email = "test@test.com"
    password = "test"
    student_id = "123000"
    quantity = 1
    reg_username = os.environ.get("reg_username", "")
    admin_username = os.environ.get("admin_username", "")
    admin_auth_token = os.environ.get("admin_auth_token", "")

    # Various error scenarios
    duplicate_name_result = client.execute(checkout_item % (reg_username, email,
                                                            password, student_id, item_name,
                                                            quantity))
    duplicate_student_id_result = client.execute(checkout_item % (username, email, password,
                                                                 'studentid0', item_name,
                                                                 quantity))
    no_username_result = client.execute(checkout_item % ("", email, password, student_id,
                                                         item_name, quantity))
    no_studentid_result = client.execute(checkout_item % (username, email, password, "",
                                                          item_name, quantity))

    assert 'please provide an e-mail and student ID.' in no_studentid_result['errors'][0]['message']
    assert 'you should enter a username' in no_username_result['errors'][0]['message']
    assert 'You should log in' in duplicate_name_result['errors'][0]['message']
    assert 'student ID is already registered' in duplicate_student_id_result['errors'][0]['message']

    # Valid scenario
    valid_user_result = client.execute(checkout_item % (username, email, password, student_id,
                                                        item_name, quantity))
    assert valid_user_result['data']['checkOutItem']['items'][0]['name'] == item_name

    # Another error scenario: while we're at it,
    # let's also try checking out an item when it's out of stock.
    no_more_quantity_result = client.execute(checkout_item_loggedin % (admin_username, item_name,
                                                                       quantity, admin_auth_token))
    assert 'Item not available.' in no_more_quantity_result['errors'][0]['message']


def test_transactions__show_transactions():
    """
    Tests that an authenticated user an only see their transactions,
    while an administrator can see all transactions.
    """
    pass


def test_transactions__accept_checkout_request():
    """
    Tests that a checkout request can be accepted by an administrator but
    not by a regular user.
    """
    pass


def test_transactions__checkin_item():
    """
    Final test in the chain of "transaction" tests.
    
    Tests that an administrator can check items back in, but a regular
    user can not.
    """
    pass


def test_authentication__login_user(clear_db, create_user_account, create_admin_account):
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


def test_authentication__validate_token(clear_db, create_user_account, create_admin_account):
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
