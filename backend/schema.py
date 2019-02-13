import bcrypt
from datetime import datetime
import graphene
from graphql_relay.node.node import from_global_id
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
import os
from tables import Item, Transaction, User, Blacklist

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
    auth_token: Authentication token
    """
    class Arguments:
        username = graphene.String(required=True)
        item_name = graphene.String(required=True)
        quantity = graphene.Int(required=True)
        auth_token = graphene.String(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, username, item_name, quantity, auth_token):
        item = Item.query.filter_by(name=item_name).first()
        user = User.query.filter_by(name=username).first()
        # Check if the item already exists
        if item:
            raise Exception("Already found one of this item...")

        # Check that the user is authenticated as an administrator
        if not validate_authentication(user, auth_token, admin=True):
            raise Exception(err_auth)

        item = Item(name=item_name, quantity=quantity, date_in=datetime.now())
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
        username = graphene.String(required=True)
        auth_token = graphene.String(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, item_name, username, auth_token):
        # Check if the item exists
        items = Item.query.filter_by(name=item_name).all()
        if not items:
            raise Exception(f"No item with the name {name} found!")

        user = User.query.filter_by(name=username).first()
        # Check if the user is authenticated
        if not validate_authentication(user, auth_token, admin=True):
            raise Exception(err_auth)

        # Delete the item
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
        if validate_authentication(user, auth_token):
            if user.admin:
                transactions = Transaction.query.all()
            else:
                transactions = Transaction.query.filter_by(user_requested_id=user.student_id).all()
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
        if not user:
            if not password:
                raise Exception("You do not have an account, so you should enter a password to create one.")
            if not email or not student_id:
                raise Exception("To create an account, please provide an e-mail and student ID.")
            encryped_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = User(name=requested_by, email=email, student_id=student_id, password=encryped_password,
                        admin=False, date_created=time_now)
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
    user_accepted_name: Name of the administrator accepting a checkout request
    item: Name of the item being requested.
    auth_token: Authentication token associated to the administrator user.
    """
    class Arguments:
        user_requested_id = graphene.String(required=True)
        transaction_id = graphene.String(required=True)
        user_accepted_name = graphene.String(required=True)
        item = graphene.String(required=True)
        auth_token = graphene.String(required=True)
    
    transactions = graphene.List(TransactionObject)

    def mutate(self, _, user_requested_id, transaction_id, user_accepted_name, item, auth_token):
        # Find the user requesting the item
        _, transaction_id = from_global_id(transaction_id)
        user_requested = User.query.filter_by(student_id=user_requested_id).first()
        if not user_requested:
            # This should never happen because the requested user's account is created
            # whenever a request is made
            raise Exception("The user that has requested this item doesn't exist ... ?")

        # Find the user accepting the request and ensure they are an authenticated administrator
        user_accepted = User.query.filter_by(name=user_accepted_name).first()
        if not validate_authentication(user_accepted, auth_token, admin=True):
            raise Exception(err_auth)

        # Find the item the user requests
        print(item)
        item = Item.query.filter_by(name=item).first()
        if not item:
            raise Exception("Item not found...")

        # Find the transaction associated with the user's checkout request
        transaction = Transaction.query.filter_by(id=transaction_id).first()
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
        if not validate_authentication(user, auth_token, admin=True):
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

        # Create a user unless one already exists by the same student ID.
        user = User.query.filter_by(student_id=student_id).first()
        if user:
            raise Exception("User already exists!")

        # Encrypt password and add user to database
        encryped_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(name=username, email=email, password=encryped_password, student_id=student_id, admin=admin)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print(e)
            session.rollback()
            raise Exception("Creation failed...")

        auth_token = encode_auth_token(user.student_id)
        return RegisterUser(auth_token.decode())


class ChangePassword(graphene.Mutation):
    """
    Changes a authenticated user's password

    Arguments:
    username: User's name
    password: User's password
    auth_token: Token to validate that the user is currently logged in
    """
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        auth_token = graphene.String(required=True)

    auth_token = graphene.Field(graphene.String)

    def mutate(self, _, username, password, auth_token):
        # Find the user in the database
        user = User.query.filter_by(name=username).first()

        # Verify that the username is valid and that the password matches
        if validate_authentication(user, auth_token):
            user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        else:
            raise Exception("Failed to authenticate user.")

        blacklisted_token = Blacklist(user_id=user.student_id, blacklisted_token=auth_token, blacklisted_at=datetime.now())
        try:
            db.session.add(blacklisted_token)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise Exception(f"Couldn't blacklist {blacklisted_token}")
        
        # Renew authentication token
        auth_token = encode_auth_token(user.student_id).decode()
        return ChangePassword(auth_token)


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
            auth_token = encode_auth_token(user.student_id)
            if auth_token:
                return LogInUser(auth_token.decode())
            else:
                raise Exception("Couldn't provide a token, please try again...")
        else:
            raise Exception("Failed to authenticate user.")


class LogOutUser(graphene.Mutation):
    """
    Logs out user by adding their authentication token to a black list.
    This function returns a string representing the logout status.

    Arguments:
    username: User's name
    password: User's password
    """
    class Arguments:
        auth_token = graphene.String(required=True)

    status = graphene.Field(graphene.String)

    def mutate(self, _, auth_token):
        user_id = decode_auth_token(auth_token)
        user = User.query.filter_by(student_id=user_id).first()
        # The token should get decoded into an integer representing the user's ID
        if not user or not validate_authentication(user, auth_token):
            raise Exception("User is not logged in...")
        blacklisted_token = Blacklist(user_id=user_id, blacklisted_token=auth_token, blacklisted_at=datetime.now())
        status = "success"
        try:
            db.session.add(blacklisted_token)
            db.session.commit()
        except Exception as e:
            print(e)
            status = "failure"
        finally:
            return LogOutUser(status)


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

    valid = graphene.Field(graphene.Int)

    def mutate(self, _, auth_token, username):
        decoded_token_id = decode_auth_token(auth_token)
        user = User.query.filter_by(name=username).first()
        is_valid = 1 if user and validate_authentication(user, auth_token) else 0
        if is_valid == 1:
            is_valid = 2 if validate_authentication(user, auth_token, admin=True) else is_valid
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
    logout_user = LogOutUser.Field()
    change_password = ChangePassword.Field()
    validate_token = ValidateToken.Field()


def validate_authentication(user, auth_token, admin=False):
    """
    Simple helper method to validate a user's authentication.

    To be authenticated, a user must have an authentication token that is neither
    expired nor on the blacklist. If the operation requires administrator privileges,
    then the user must be an administrator in addition to being authenticated.
    """
    blacklisted_token = Blacklist.query.filter_by(user_id=user.student_id,
                                                  blacklisted_token=auth_token).first()
    is_authenticated = not blacklisted_token and user and user.student_id == decode_auth_token(auth_token)

    if admin:
        return is_authenticated and user.admin
    return is_authenticated