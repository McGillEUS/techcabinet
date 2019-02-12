import bcrypt
from datetime import datetime
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
import os
from tables import Item, Transaction, User

from utils import db, encode_auth_token, decode_auth_token


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


class Query(graphene.ObjectType):
    """
    Basic Query object.
    """
    node = graphene.relay.Node.Field()
    all_items = SQLAlchemyConnectionField(ItemObject)


class CreateItem(graphene.Mutation):
    """
    Creates an Item.
    Used for administrative and testing purposes, as users shall not
    be allowed to create products.

    Arguments:
    name: Name of item.
    quantity: Quantity of item available
    """
    class Arguments:
        name = graphene.String(required=True)
        quantity = graphene.Int(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, name, quantity):
        item = Item.query.filter_by(name=name).first()
        if item:
            raise Exception("Already found one of this item...")
        item = Item(name=name, quantity=quantity, date_in=datetime.now())
        db.session.add(item)
        db.session.commit()
        items = Item.query.all()
        return CreateItem(items=items)


class DeleteItem(graphene.Mutation):
    """
    Deletes an Item.

    Arguments:
    name: Name of item
    """
    class Arguments:
        name = graphene.String(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, name):
        items = Item.query.filter_by(name=name).all()
        if not items:
            raise Exception(f"No item with the name {name} found!")
        for item in items:
            db.session.delete(item)
        db.session.commit()
        items = Item.query.all()
        return DeleteItem(items=items)


class ShowItems(graphene.Mutation):
    """
    Shows all items in the database.

    These are visible to anyone using the platform.
    """
    items = graphene.List(ItemObject)

    def mutate(self, _):
        items = Item.query.all()
        return ShowItems(items=items)


class ShowTransactions(graphene.Mutation):
    """
    Shows all transactions in the database to an authenticated user.
    Administrators can view all transactions, while regular users can only
    view their personal transactions.

    Arguments:
    username: Username of the user requesting to view transactions.
    auth_token: Authentication token (hopefully) associated to this user.
    """
    class Arguments:
        username = graphene.String(required=True)
        auth_token = graphene.String(required=True)

    transactions = graphene.List(TransactionObject)

    def mutate(self, _, username, auth_token):
        user = User.query.filter_by(name=username).first()
        transactions = []
        if user and user.id = decode_auth_token(auth_token):
            if user.admin:
                transactions = Transaction.query.all()
            else:
                transactions = Transaction.query.filter_by(user_requested_id=user.id).all()
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
        email = graphene.String(required=True)
        student_id = graphene.String(required=True)
        quantity = graphene.Int(required=True)
        item_name = graphene.String(required=True)
        auth_token = graphene.String()
        password = graphene.String()

    items = graphene.List(ItemObject)

    def mutate(self, _, requested_by, email, student_id, quantity, password, item_name):
        # Verify that the quantity the user wishes to check out is valid
        if quantity < 0:
            raise Exception("Positive quantities only.")

        # If no account exists, create one, else authenticate the user.
        user = User.query.filter_by(name=requested_by, email=email, student_id=student_id).first()
        if not user:
            if not password:
                raise Exception("You do not have an account, so you should enter a password to create one.")
            user = User(name=requested_by, email=email, student_id=student_id, password=password)
            db.session.add(user)
        else:
            if not auth_token or user.id != decode_auth_token(auth_token):
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
        transaction = Transaction(user_requested_id=user.id, requested_quantity=quantity, item_id=item.id, date_requested=datetime.now(), accepted=False)
        db.session.add(transaction)
        db.session.commit()
        items = Item.query.all()
        return CheckOutItem(items)


class AcceptCheckoutRequest(graphene.Mutation):
    """
    Authenticated administrator users are able to accept a request to check out items.

    Arguments:
    user_requested_id: ID of the user requesting an item
    user_accepted_name: Name of the administrator accepting a checkout request
    item_id: ID of the item being requested.
    auth_token: Authentication token associated to the administrator user.
    """
    class Arguments:
        user_requested_id = graphene.Int(required=True)
        user_accepted_name = graphene.String(required=True)
        item_id = graphene.Int(required=True)
        auth_token = graphene.String(required=True)
    
    transactions = graphene.List(TransactionObject)

    def mutate(self, _, user_requested_id, user_accepted_name, item_id, auth_token):
        # Find the user requesting the item
        user_requested = User.query.filter_by(id=user_requested_id).first()
        if not user_requested:
            # This should never happen because the requested user's account is created
            # whenever a request is made
            raise Exception("The user that has requested this item doesn't exist ... ?")

        # Find the user accepting the request and ensure they are an authenticated administrator
        user_accepted = User.query.filter_by(name=user_accepted_name).first()
        if not user_accepted or not user_accepted.admin or user_accepted.id != decode_auth_token(auth_token):
            raise Exception(err_auth)

        # Find the item the user requests
        item = Item.query.filter_by(id=item_id).first()
        if not item:
            raise Exception("Item not found...")

        # Find the transaction associated with the user's checkout request
        transaction = Transaction.query.filter_by(user_requested_id=user_requested_id, accepted=False, item_id=item.id).first()
        if not transaction:
            raise Exception("No such transaction found...")

        # Update the transaction to track the item as checked out
        transaction.accepted = True
        transaction.user_accepted = user_accepted_name
        transaction.date_accepted = datetime.now()
        item.date_out = transaction.date_accepted
        transactions = Transaction.query.all()
        return AcceptCheckoutRequest(transactions=transactions)


class CheckInItem(graphene.Mutation):
    """
    Authenticated administrators are able to accept a request to check items back in.

    Arguments:
    item_id: The ID of the item which had been previously checked out
    admin_name: The name of the administrator checking the item back in
    quantity: Quantity of the item which had been checked out
    auth_token: Authentication token associated with the administrator user
    """
    class Arguments:
        item_id = graphene.String(required=True)
        admin_name = graphene.String(required=True)
        quantity = graphene.Int(required=True)
        auth_token = graphene.String(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, item_id, admin_name, quantity, auth_token):
        # Validate that the user is not attempting to check in invalid quantities
        if quantity < 0:
            raise Exception("Positive quantities only.")

        # Authenticate the user
        user = User.query.filter_by(name=admin_name).first()
        if not user or not user.admin or user.id != decode_auth_token(auth_token):
            raise Exception(err_auth)

        # Check the item back in
        item = Item.query.filter_by(name=name).first()
        item.user_out = None
        item.date_out = None
        item.date_in = datetime.now()
        item.quantity += quantity
        items = Item.query.all()
        return CheckInItem(items)


class RegisterUser(graphene.Mutation):
    """
    Registers user to database.
    This is not exposed to users as it would allow them to create administrator accounts.

    Arguments:
    username: New user's name
    email: New user's email
    password: New user's password
    student_id: New user's student ID
    admin: Whether this new user is an admin or not
    supersecretpassword: Validates that only supreme administrators are using this.
    """
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        student_id = graphene.String(required=True)
        admin = graphene.Boolean(required=True)
        supersecretpassword = graphene.String(required=True)

    auth_token = graphene.Field(graphene.String)

    def mutate(self, _, username, email, password, student_id, admin, supersecretpassword):
        # Only the most exclusive administrators have access to this end-point.
        if os.environ.get("supersecretpassword") != supersecretpassword:
            raise Exception("You are not allowed to perform this action...")

        # Create a user unless one already exists by that name.
        user = User.query.filter_by(name=username, email=email, student_id=student_id).first()
        if user:
            raise Exception("User already exists!")

        # Encrypt password and add user to database
        encryped_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(name=username, email=email, password=encryped_password, student_id=student_id, admin=admin)
        db.session.add(user)
        db.session.commit()
        auth_token = encode_auth_token(user.id)
        return RegisterUser(auth_token.decode())


class LogInUser(graphene.Mutation):
    """
    Logs in user

    Arguments:
    username: User's name
    password: User's password
    """
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    auth_token = graphene.Field(graphene.String)

    def mutate(self, _, username, password):
        # Find the user in the database
        user = User.query.filter_by(name=username).first()

        # Verify that the username is valid and that the password matches
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            auth_token = encode_auth_token(user.id)
            if auth_token:
                return LogInUser(auth_token.decode())
            else:
                raise Exception("Couldn't provide a token, please try again...")
        else:
            raise Exception("Failed to authenticate user.")


class ValidateToken(graphene.Mutation):
    """
    Vaildates that an authentication token belongs to a given user and is not expired.

    Arguemnts:
    auth_token: Authentication token
    username: User's name
    """
    class Arguments:
        auth_token = graphene.String(required=True)
        username = graphene.String(required=True)

    valid = graphene.Field(graphene.Boolean)

    def mutate(self, _, auth_token, username):
        decoded_token_id = decode_auth_token(auth_token)
        user = User.query.filter_by(name=username).first()
        is_valid = user and decoded_token_id == user.id
        return ValidateToken(is_valid)


class Mutation(graphene.ObjectType):
    """
    Defines all available mutations.
    """
    create_item = CreateItem.Field()
    delete_item = DeleteItem.Field()
    show_items = ShowItems.Field()
    check_out_item = CheckOutItem.Field()
    check_in_item = CheckInItem.Field()
    accept_checkout_request = AcceptCheckoutRequest.Field()
    show_transactions = ShowTransactions.Field()
    register_user = RegisterUser.Field()
    login_user = LogInUser.Field()
    validate_token = ValidateToken.Field()
