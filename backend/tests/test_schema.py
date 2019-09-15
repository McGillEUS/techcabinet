from graphene.test import Client
from mock import MagicMock, patch
import os
import jwt
import sys
import time

from queries import query_items, create_item, delete_item, checkout_item, show_transactions, \
                    checkin_item, create_admin, reserve_item

sys.path.insert(0, os.getcwd())
from schema import schema, err_auth, err_auth_admin

client = Client(schema)
item_name = "potato"
admin_email = "admin@mail.com"
email = "email"


def test_inventory__show_and_create_items(clear_db):
    """
    Tests possibility to display items
    """
    result = client.execute(query_items)
    assert 'data' in result
    assert 'allItems' in result['data']
    assert 'edges' in result['data']['allItems']
    assert type(result['data']['allItems']['edges']) == list


@patch('schema.auth_level')
def test_inventory__create_item(auth_level, clear_db):
    """
    Tests whether it is possible to create an item
    """
    quantity = 1
    client.execute(create_admin % (admin_email, "admin", ""))

    # It should be impossible to create an item without being logged in
    auth_level.return_value = 0
    result = client.execute(create_item % (item_name, quantity, ""))
    assert 'errors' in result
    assert err_auth_admin in result['errors'][0]['message']

    # It should be impossible to create an item without being an administrator
    auth_level.return_value = 1
    result = client.execute(create_item % (item_name, quantity,  ""))
    assert 'errors' in result
    assert err_auth_admin in result['errors'][0]['message']

    # It should be possible to create an item as an administrator
    auth_level.return_value = 2
    result = client.execute(create_item % (item_name, quantity,  admin_email))
    assert 'errors' not in result
    assert result['data']['createItem']['items'][0]['name'] == item_name


@patch('schema.auth_level')
def test_inventory__delete_item(auth_level, clear_db):
    """
    Tests possibility to delete items
    """
    quantity = 1

    # First, create the item. Previous test validates that this is possible.
    auth_level.return_value = 2
    client.execute(create_admin % (admin_email, "admin", ""))
    result = client.execute(create_item % (item_name, quantity, admin_email))

    # It should be impossible to delete an item without being logged in
    auth_level.return_value = 0
    result = client.execute(delete_item % (item_name, admin_email))
    assert 'errors' in result
    assert err_auth_admin in result['errors'][0]['message']

    # It should be impossible to delete an item without being an administrator
    auth_level.return_value = 1
    result = client.execute(delete_item % (item_name, admin_email))
    assert 'errors' in result
    assert err_auth_admin in result['errors'][0]['message']

    # It should be possible to delete an item as an administrator
    auth_level.return_value = 2
    result = client.execute(delete_item % (item_name, admin_email))
    assert 'errors' not in result
    assert len(result['data']['deleteItem']['items']) == 0

    # It should be impossible to delete an item if it doesn't exist
    auth_level.return_value = 2
    result = client.execute(delete_item % (item_name, admin_email))
    assert 'errors' in result


@patch('schema.auth_level')
def test_transactions__reserve_item(auth_level, clear_db):
    """
    Tests that an authenticated user can create transactions by checking
    out an item, but that a non-authenticated user can not.

    This test is linked with the next four tests.
    """
    quantity = 3

    # First, create the item.
    auth_level.return_value = 2
    client.execute(create_admin % (admin_email, "admin", ""))
    result = client.execute(create_item % (item_name, quantity, admin_email))

    quantity = 1

    # Next, attempt to check out the item as a user with invalid credentials
    auth_level.return_value = 0
    invalid_email_or_token_result = client.execute(reserve_item % (email, "123123123", item_name, quantity))
    assert 'errors' in invalid_email_or_token_result
    assert err_auth in invalid_email_or_token_result['errors'][0]['message']

    # Now attempt to check out the item as a user with valid credentials
    auth_level.return_value = 1
    regular_user_result = client.execute(reserve_item % (email, "123123123", item_name, quantity))
    assert 'data' in regular_user_result
    assert regular_user_result['data']['reserveItem']['items'][0]['name'] == item_name

    # Now attempt to check out the item as an admin
    auth_level.return_value = 2
    admin_result = client.execute(reserve_item % (admin_email, "123123123", item_name, quantity))
    assert 'data' in admin_result
    assert admin_result['data']['reserveItem']['items'][0]['name'] == item_name


@patch('schema.auth_level')
def test_transactions__show_transactions(auth_level):
    """
    Tests that an authenticated user an only see their transactions,
    while an administrator can see all transactions.
    """
    # Invalid scenario: no user
    auth_level.return_value = 0
    no_user_result = client.execute(show_transactions % (email))
    assert len(no_user_result['data']['showTransactions']['transactions']) == 0

    # Valid scenario : regular user
    auth_level.return_value = 1
    regular_user_result = client.execute(show_transactions % (email))
    assert len(regular_user_result['data']['showTransactions']['transactions']) == 1

    # Valid scenario : administrator
    auth_level.return_value = 2
    admin_user_result = client.execute(show_transactions % (admin_email))
    assert len(admin_user_result['data']['showTransactions']['transactions']) == 2


@patch('schema.auth_level')
def test_transactions__checkout_item(auth_level):
    """
    Tests that a checkout request can be accepted by an administrator but
    not by a regular user.
    """
    auth_level.return_value = 1
    regular_user_transactions = client.execute(show_transactions % (email))
    transaction_id = regular_user_transactions['data']['showTransactions']['transactions'][0]['id']

    # Invalid scenario: regular users can not accept checkout requests
    regular_user_result = client.execute(checkout_item % (transaction_id, email, item_name))
    assert err_auth_admin in regular_user_result['errors'][0]['message']

    # Valid scenario: administrators can accept checkout requests
    auth_level.return_value = 2
    admin_user_result = client.execute(checkout_item % (transaction_id, admin_email, item_name))
    assert admin_user_result['data']['checkOutItem']['transactions'][0]['adminAccepted'] == admin_email


@patch('schema.auth_level')
def test_transactions__checkin_item(auth_level):
    """
    Final test in the chain of "transaction" tests.
    
    Tests that an administrator can check items back in, but a regular
    user can not.
    """
    auth_level.return_value = 1
    regular_user_transactions = client.execute(show_transactions % (email))
    transaction_id = regular_user_transactions['data']['showTransactions']['transactions'][0]['id']

    # Invalid scenario: regular users can not check items back in (...yet)
    regular_user_result = client.execute(checkin_item % (email, transaction_id, item_name))
    assert err_auth_admin in regular_user_result['errors'][0]['message']

    # Valid scenario : administrators can always check items back in
    auth_level.return_value = 2
    admin_user_result = client.execute(checkin_item % (admin_email, transaction_id, item_name))
    assert admin_user_result['data']['checkInItem']['transactions'][0]['returned']

