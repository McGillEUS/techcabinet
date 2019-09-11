import bcrypt
from datetime import datetime
import graphene
from graphql_relay.node.node import from_global_id
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
import os
from tables import Item, Transaction, Admin

from utils import db


err_auth = "You must be an authenticated administrator!"


class ItemObject(SQLAlchemyObjectType):
    """
    Maps to `Item` table in Database.
    """
    class Meta:
        model = Item
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

        # Check that the user is authenticated as an administrator
        if not validate_authentication(email, auth_token):
            raise Exception(err_auth)

        item = Item(name=item_name, quantity=quantity, date_in=datetime.now(), created_by=email)
        db.session.add(item)
        db.session.commit()
        items = Item.query.all()
        return CreateItem(items=items)


class DeleteItem(graphene.Mutation):
    """
    Deletes an Item. This is reserved for administrators.

    Arguments:
    name: Name of item
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

        user = User.query.filter_by(name=email).first()
        # Check if the user is authenticated
        if not validate_authentication(user, auth_token):
            raise Exception(err_auth)

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
        user_auth_level = validate_authentication(email, auth_token)
        transactions = Transaction.query.all() if user_auth_level > 1 else Transaction.query.filter_by(user_requested_email=email).all()
        return ShowTransactions(transactions=transactions)


class CheckOutItem(graphene.Mutation):
    """
    Basic logic for checking out items.
    This creates a checkout request which needs to be approved by an administrator.

    A user account is created whenever someone attempts to check out an item.
    If an account already exists for a user, they are asked to log in before continuing,
    or simply to create an account by providing an e-mail with their checkout request.

    Arguments:
    requested_by: Name of the person requestion to check out an item
    email: Email of the same person
    student_id: Student ID of the same person
    quantity: Quantity of the item requested
    item_name: Name of the item requested from the inventory
    """
    class Arguments:
        requested_by = graphene.String(required=True)
        quantity = graphene.Int(required=True)
        item_name = graphene.String(required=True)
        auth_token = graphene.String(required=False)
        email = graphene.String()
        student_id = graphene.String()
        password = graphene.String()

    items = graphene.List(ItemObject)

    def mutate(self, _, requested_by, quantity, item_name, auth_token, email, student_id, password):
        # Verify that the quantity the user wishes to check out is valid
        if quantity < 0:
            raise Exception("Positive quantities only.")

        # If no account exists, create one, else authenticate the user.
        user = User.query.filter_by(name=requested_by).first()
        time_now = datetime.now()
        # TODO: This should be redone, we only care about having a logged in user

        # We make sure the user's name doesn't exist
        if not user:
            # We make sure the user gave a password, email and student ID
            if not password or not requested_by:
                raise Exception("You do not have an account, so you should enter a email & password to create one.")
            if not email or not student_id:
                raise Exception("To create an account, please provide an e-mail and student ID.")

            # We make sure the user's student ID doesn't already correspond to an existing user
            user = User.query.filter_by(student_id=student_id).first()

            # We encrypt the user's password and create an account.
            encryped_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            if not user:
                user = User(name=requested_by, email=email, student_id=student_id, password=encryped_password,
                            admin=False, date_created=time_now)
            else:
                raise Exception("This student ID is already registered!")

            try:
                db.session.add(user)
            except Exception as e:
                print(e)
                db.session.rollback()
        else:
            if not validate_authentication(user, auth_token):
                raise Exception("You should log in as you have an account! Feel free to create one otherwise.")

        # Find the item the user requests
        item = Item.query.filter_by(name=item_name).first()
        if not item:
            raise Exception("Item not found...")

        # Validate that the item is available in sufficient quantities
        if item.quantity - quantity < 0:
            db.session.commit()
            raise Exception("Item not available.")

        # Update the item's state as it is requested
        item.quantity -= quantity
        transaction = Transaction(user_requested_id=user.student_id, requested_quantity=quantity, item=item.name, date_requested=time_now, accepted=False)
        db.session.add(transaction)
        db.session.commit()
        items = Item.query.all()
        return CheckOutItem(items)


class AcceptCheckoutRequest(graphene.Mutation):
    """
    Authenticated administrator users are able to accept a request to check out items.

    Arguments:
    user_requested_id: ID of the user requesting an item
    admin_accepted_name: Name of the administrator accepting a checkout request
    item: Name of the item being requested.
    auth_token: Authentication token associated to the administrator user.
    """
    class Arguments:
        user_requested_id = graphene.String(required=True)
        transaction_id = graphene.String(required=True)
        admin_accepted_name = graphene.String(required=True)
        item = graphene.String(required=True)
        auth_token = graphene.String(required=True)
    
    transactions = graphene.List(TransactionObject)

    def mutate(self, _, user_requested_id, transaction_id, admin_accepted_name, item, auth_token):
        # Find the user requesting the item
        _, transaction_id = from_global_id(transaction_id)
        user_requested = User.query.filter_by(student_id=user_requested_id).first()
        if not user_requested:
            # This should never happen because the requested user's account is created
            # whenever a request is made
            raise Exception("The user that has requested this item doesn't exist ... ?")

        # Find the user accepting the request and ensure they are an authenticated administrator
        admin_accepted = User.query.filter_by(name=admin_accepted_name).first()
        if not validate_authentication(admin_accepted, auth_token):
            raise Exception(err_auth)

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
        transaction.admin_accepted = admin_accepted_name
        transaction.date_accepted = datetime.now()
        item.date_out = transaction.date_accepted
        transactions = Transaction.query.all()
        return AcceptCheckoutRequest(transactions=transactions)


class CheckInItem(graphene.Mutation):
    """
    Authenticated administrators are able to accept a request to check items back in.

    Arguments:
    item: Name of the item being requested.
    admin_name: The name of the administrator checking the item back in
    quantity: Quantity of the item which had been checked out
    auth_token: Authentication token associated with the administrator user
    """
    class Arguments:
        item = graphene.String(required=True)
        transaction_id = graphene.String(required=True)
        admin_name = graphene.String(required=True)
        auth_token = graphene.String(required=True)

    transactions = graphene.List(TransactionObject)

    def mutate(self, _, item, transaction_id, admin_name, auth_token):
        # Authenticate the user
        user = User.query.filter_by(name=admin_name).first()
        if not validate_authentication(user, auth_token):
            raise Exception(err_auth)

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


class ValidateToken(graphene.Mutation):
    """
    Vaildates that an authentication token belongs to a given user and is not expired.

    Arguemnts:
    auth_token: Authentication token
    email: User's unique email
    """
    class Arguments:
        auth_token = graphene.String(required=True)
        email = graphene.String(required=True)

    valid = graphene.Field(graphene.Int)

    def mutate(self, _, auth_token, email):
        # TODO: This should validate the tokens given by Outlook's oauth
        return ValidateToken(1)


class Mutation(graphene.ObjectType):
    """
    Defines all available mutations (Create, Update, Delete).
    """
    create_item = CreateItem.Field()
    delete_item = DeleteItem.Field()
    check_out_item = CheckOutItem.Field()
    check_in_item = CheckInItem.Field()
    accept_checkout_request = AcceptCheckoutRequest.Field()
    show_transactions = ShowTransactions.Field()
    validate_token = ValidateToken.Field()


class Query(graphene.ObjectType):
    """
    Defines all available queries (Read).
    """
    node = graphene.relay.Node.Field()
    all_items = SQLAlchemyConnectionField(ItemObject)

def validate_authentication(email, auth_token):
    """
    Simple helper method to validate a user's authentication.

    To be authenticated, a user must have an authentication token that is neither
    expired nor on the blacklist. If the operation requires administrator privileges,
    then the user must be an administrator in addition to being authenticated.
    """
    if not email or not auth_token:
        return False
    # TODO: Validate token. If token is valid, return true

    #if admin:
    #    userCount = Admin.query.filter_by(email=email).count()
    #    return userCount == 1
    return True

schema = graphene.Schema(query=Query, mutation=Mutation)