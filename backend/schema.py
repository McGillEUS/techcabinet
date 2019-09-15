import base64
from datetime import datetime
import graphene
from graphql_relay.node.node import from_global_id
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
import json
import os
import requests
from tables import Item, Transaction, Admin

from utils import db, supersecretpassword


err_auth_admin = "You must be an authenticated administrator!"
err_auth = "You must log in to perform this action."


class ItemObject(SQLAlchemyObjectType):
    """
    Maps to `Item` table in Database.
    """
    class Meta:
        model = Item
        interfaces = (graphene.relay.Node, )


class AdminObject(SQLAlchemyObjectType):
    """
    Maps to `Admin` table in Database.
    """
    class Meta:
        model = Admin
        interfaces = (graphene.relay.Node, )


class TransactionObject(SQLAlchemyObjectType):
    """
    Maps to `Transaction` table in Database.
    """
    class Meta:
        model = Transaction
        interfaces = (graphene.relay.Node, )


class CreateItem(graphene.Mutation):
    """
    Creates an Item.
    Used for administrative and testing purposes, as users shall not
    be allowed to create products.

    Arguments:
    name: Name of item.
    quantity: Quantity of item available
    auth_token: Authentication token
    """
    class Arguments:
        email = graphene.String(required=True)
        item_name = graphene.String(required=True)
        quantity = graphene.Int(required=True)
        auth_token = graphene.String(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, email, item_name, quantity, auth_token):
        item = Item.query.filter_by(name=item_name).first()
        # Check if the item already exists
        if item:
            raise Exception("Already found one of this item...")
            
        validate_authentication(email, auth_token, admin=True)
        item = Item(name=item_name, quantity=quantity, date_in=datetime.now(), created_by=email)
        db.session.add(item)
        db.session.commit()
        items = Item.query.all()
        return CreateItem(items=items)


class DeleteItem(graphene.Mutation):
    """
    Deletes an Item. This is reserved for administrators.

    Arguments:
    item_name: Name of item
    email: Email of user performing the action
    auth_token: Authentication token
    """
    class Arguments:
        item_name = graphene.String(required=True)
        email = graphene.String(required=True)
        auth_token = graphene.String(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, item_name, email, auth_token):
        # Check if the item exists
        items = Item.query.filter_by(name=item_name).all()
        if not items:
            raise Exception(f"No item with the name {name} found!")

        validate_authentication(email, auth_token, admin=True)

        # Delete the item
        for item in items:
            db.session.delete(item)
        db.session.commit()
        items = Item.query.all()
        return DeleteItem(items=items)


class ShowTransactions(graphene.Mutation):
    """
    Shows all transactions in the database to an authenticated user.
    Administrators can view all transactions, while regular users can only
    view their personal transactions.

    Arguments:
    email: email of the user requesting to view transactions.
    auth_token: Authentication token (hopefully) associated to this user.
    """
    class Arguments:
        email = graphene.String(required=True)
        auth_token = graphene.String(required=True)

    transactions = graphene.List(TransactionObject)

    def mutate(self, _, email, auth_token):
        transactions = []
        if auth_level(email, auth_token) == 2:
            transactions = Transaction.query.all()
        elif auth_level(email, auth_token) == 1:
            transactions = Transaction.query.filter_by(user_requested_email=email).all()

        return ShowTransactions(transactions=transactions)


class ReserveItem(graphene.Mutation):
    """
    Basic logic for reserving items.
    This creates a reservation which needs to be approved by an administrator when the item is checked out.

    Arguments:
    email: Email of the person requesting the item
    student_id: Student ID of the same person
    auth_token: Token used to authenticate
    quantity: Quantity of the item requested
    item_name: Name of the item requested from the inventory
    """
    class Arguments:
        email = graphene.String()
        student_id = graphene.String()
        auth_token = graphene.String(required=False)
        quantity = graphene.Int(required=True)
        item_name = graphene.String(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, email, student_id, auth_token, quantity, item_name):
        # Verify that the quantity the user wishes to check out is valid
        if quantity < 0:
            raise Exception("Positive quantities only.") 

        validate_authentication(email, auth_token)

        # Find the item the user requests
        item = Item.query.filter_by(name=item_name).first()
        if not item:
            raise Exception("Item not found...")

        # Validate that the item is available in sufficient quantities
        if item.quantity - quantity < 0:
            db.session.commit()
            raise Exception("Item not available in sufficient quantities.")

        # Update the item's state as it is requested
        item.quantity -= quantity

        transaction = Transaction(
            user_requested_id=student_id,
            user_requested_email=email,
            requested_quantity=quantity,
            item=item.name,
            date_requested=datetime.now(),
            accepted=False
        )

        db.session.add(transaction)
        db.session.commit()
        items = Item.query.all()
        return ReserveItem(items)


class CheckOutItem(graphene.Mutation):
    """
    Authenticated administrator users are able to accept a request to check out items.

    Arguments:
    transaction_id: ID of the transaction that took place to reserve the item
    item: Name of the item being requested.
    admin_email: Email of the administrator accepting a checkout request
    auth_token: Authentication token associated to the administrator user.
    """
    class Arguments:
        transaction_id = graphene.String(required=True)
        admin_email = graphene.String(required=True)
        item = graphene.String(required=True)
        auth_token = graphene.String(required=True)

    transactions = graphene.List(TransactionObject)

    def mutate(self, _, transaction_id, item, admin_email, auth_token):
        _, transaction_id = from_global_id(transaction_id)

        validate_authentication(admin_email, auth_token, admin=True)

        admin_accepting = Admin.query.filter_by(email=admin_email).first()

        # Find the item the user requests
        item = Item.query.filter_by(name=item).first()
        if not item:
            raise Exception("Item not found...")

        # Find the transaction associated with the user's checkout request
        transaction = Transaction.query.filter_by(id=transaction_id).first()

        if not transaction:
            raise Exception("No such transaction found...")

        # Update the transaction to track the item as checked out
        transaction.accepted = True
        transaction.admin_accepted = admin_email
        transaction.date_accepted = datetime.now()
        item.date_out = transaction.date_accepted
        transactions = Transaction.query.all()
        return CheckOutItem(transactions=transactions)


class CheckInItem(graphene.Mutation):
    """
    Authenticated administrators are able to accept a request to check items back in.

    Arguments:
    item: Name of the item being requested.
    transaction_id: ID of the transaction that took place to reserve the item
    admin_email: The name of the administrator checking the item back in
    auth_token: Authentication token associated with the administrator user
    """
    class Arguments:
        item = graphene.String(required=True)
        transaction_id = graphene.String(required=True)
        admin_email = graphene.String(required=True)
        auth_token = graphene.String(required=True)

    transactions = graphene.List(TransactionObject)

    def mutate(self, _, item, transaction_id, admin_email, auth_token):
        validate_authentication(admin_email, auth_token, admin=True)

        # Check the item back in
        _, transaction_id = from_global_id(transaction_id)
        transaction = Transaction.query.filter_by(id=transaction_id).first()
        item = Item.query.filter_by(name=item).first()
        transaction.returned = True
        transaction.date_returned = datetime.now()
        item.date_in = datetime.now()
        item.quantity += transaction.requested_quantity
        transactions = Transaction.query.all()

        return CheckInItem(transactions)


class CreateAdmin(graphene.Mutation):
    """
    Creates an Admin.

    Arguments:
    name: Full name of admin user.
    email: Email address of admin user.
    """
    class Arguments:
        email = graphene.String(required=True)
        name = graphene.String(required=True)
        password = graphene.String(required=True)

    admins = graphene.List(AdminObject)

    def mutate(self, _, email, name, password):
        if password != supersecretpassword:
          return CreateAdmin(admins=[])


        admin = Admin(email=email, name=name, date_created=datetime.now())
        db.session.add(admin)
        db.session.commit()
        admins = Admin.query.all()
        return CreateAdmin(admins=admins)


class AuthenticationLevel(graphene.Mutation):
    """
    Wrapper around the function returning a user's authentication level.

    This is only used for the front-end to display different options to administrators,
    logged in users and logged out users.

    Arguments:
    auth_token: Authentication token
    email: User's unique email
    """
    class Arguments:
        auth_token = graphene.String(required=True)
        email = graphene.String(required=True)

    level = graphene.Field(graphene.Int)

    def mutate(self, _, email, auth_token):
        return AuthenticationLevel(auth_level(email, auth_token))


class Mutation(graphene.ObjectType):
    """
    Defines all available mutations (Create, Update, Delete).
    """
    create_item = CreateItem.Field()
    delete_item = DeleteItem.Field()
    check_out_item = CheckOutItem.Field()
    check_in_item = CheckInItem.Field()
    reserve_item = ReserveItem.Field()
    show_transactions = ShowTransactions.Field()
    authentication_level = AuthenticationLevel.Field()
    create_admin = CreateAdmin.Field()


class Query(graphene.ObjectType):
    """
    Defines all available queries (Read).
    """
    node = graphene.relay.Node.Field()
    all_items = SQLAlchemyConnectionField(ItemObject)


def validate_authentication(email, auth_token, admin=False):
    if admin and auth_level(email, auth_token) < 2:
        raise Exception(err_auth_admin)
    if auth_level(email, auth_token) < 1:
        raise Exception(err_auth)


def auth_level(email, auth_token):
    """
    Authentication levels:
    0: Logged out
    1: Logged in, regular
    2: Logged in, administrator

    Authenticated users send an Access Token from the front-end.
    This token is used to query Microsoft's Graph API to get information about a user.

    If the Graph API returns a valid response (i.e.: the token is valid),
    And the response is for the same user as the one making the request,
    then the user is considered authenticated.

    If the user is part of the administrator database, the user is given more rights.
    """
    authentication_response = requests.get(
        'https://graph.microsoft.com/v1.0/me/',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    if authentication_response.status_code != 200:
        return 0

    authentication_json = json.loads(authentication_response.content)
    if authentication_json['mail'] != email:
        return 0

    if Admin.query.filter_by(email=email).count() == 1:
        return 2

    return 1

schema = graphene.Schema(query=Query, mutation=Mutation)