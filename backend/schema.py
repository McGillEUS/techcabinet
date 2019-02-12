from datetime import datetime
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from tables import Item, Transaction, User
import bcrypt
from utils import db, encode_auth_token, decode_auth_token


class ItemObject(SQLAlchemyObjectType):
    """
    Maps to `Item` table in Database.
    """
    class Meta:
        model = Item
        interfaces = (graphene.relay.Node, )


class TransactionObject(SQLAlchemyObjectType):
    """
    Maps to `Item` table in Database.
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
    Shows all items in the database
    """
    items = graphene.List(ItemObject)

    def mutate(self, _):
        items = Item.query.all()
        return ShowItems(items=items)

class ShowTransactions(graphene.Mutation):
    """
    Shows all transactions in the database
    """
    transactions = graphene.List(TransactionObject)

    def mutate(self, _):
        transactions = Transaction.query.all()
        return ShowTransactions(transactions=transactions)

class IncrementItemQuantity(graphene.Mutation):
    """
    Increments quantity of an item
    """
    class Arguments:
        name = graphene.String(required=True)
        quantity = graphene.Int(required=True)

    item = graphene.Field(lambda: ItemObject)

    def mutate(self, _, name, quantity):
        item = Item.query.filter_by(name=name).first()
        if not item:
            raise Exception(f"Item named {name} not found!")
        if item.quantity + quantity < 0:
            raise Exception(f"Item {name} not available anymore!")

        item.quantity += quantity
        return IncrementItemQuantity(item)

class CheckOutItem(graphene.Mutation):
    """
    Basic logic for checking out items
    """
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        student_id = graphene.String(required=True)
        quantity = graphene.Int(required=True)
        requested_by = graphene.String(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, name, email, student_id, quantity, requested_by):
        if quantity < 0:
            raise Exception("Positive quantities only.")

        user = User.query.filter_by(name=requested_by, email=email, student_id=student_id).first()
        if not user:
            user = User(name=requested_by, email=email, student_id=student_id)
            db.session.add(user)

        # TODO: rename "name" variable for item... kindof getting confusing.
        item = Item.query.filter_by(name=name).first()
        if not item:
            raise Exception("Item not found...")

        if item.quantity - quantity < 0:
            db.session.commit()
            raise Exception("Item not available.")
        item.quantity -= quantity
        transaction = Transaction(user_requested_id=user.id, requested_quantity=quantity, item_id=item.id, date_requested=datetime.now(), accepted=False)
        db.session.add(transaction)
        db.session.commit()
        items = Item.query.all()
        return CheckOutItem(items)


class AcceptCheckoutRequest(graphene.Mutation):
    """
    Accepting an item getting checked out
    """
    class Arguments:
        user_requested_id = graphene.Int(required=True)
        user_accepted_name = graphene.String(required=True)
        user_accepted_email = graphene.String(required=True)
        item_id = graphene.Int(required=True)
    
    transactions = graphene.List(TransactionObject)

    def mutate(self, _, user_requested_id, user_accepted_name, user_accepted_email, item_id):
        user_requested = User.query.filter_by(id=user_requested_id).first()
        if not user_requested:
            # This should never happen
            raise Exception("The user that has requested this item doesn't exist ... ?")

        # This should [maybe?] be improved to make the accepting user more unique...
        user_accepted = User.query.filter_by(name=user_accepted_name, email=user_accepted_email).first()
        if not user_accepted:
            # This should be a problem, because the accepting user should either have checked out
            # an item or be logged in, so this situation shouldn't happen...
            # Leaving it for demo purposes for now because auth isn't implemented.
            user_accepted = User(name=user_accepted, email=user_accepted_email)
            db.session.add(user_accepted)
            db.session.commit()

        item = Item.query.filter_by(id=item_id).first()
        if not item:
            raise Exception("Item not found...")
        transaction = Transaction.query.filter_by(user_requested_id=user_requested_id, accepted=False, item_id=item.id).first()
        if not transaction:
            raise Exception("No such transaction found...")
        transaction.accepted = True
        transaction.user_accepted = user_accepted_name
        transaction.date_accepted = datetime.now()
        item.date_out = transaction.date_accepted
        transactions = Transaction.query.all()
        return AcceptCheckoutRequest(transactions=transactions)


class CheckInItem(graphene.Mutation):
    """
    Basic logic for checking in items.
    This resets the "last checked out by" fields.
    """
    class Arguments:
        name = graphene.String(required=True)
        quantity = graphene.Int(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, name, quantity):
        if quantity < 0:
            raise Exception("Positive quantities only.")

        item = Item.query.filter_by(name=name).first()
        item.user_out = None
        item.date_out = None
        item.date_in = datetime.now()
        item.quantity += quantity
        items = Item.query.all()
        return CheckInItem(items)

class RegisterUser(graphene.Mutation):
    """
    Registers user to database
    """
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        student_id = graphene.String(required=True)

    auth_token = graphene.Field(graphene.String)

    def mutate(self, _, username, email, password, student_id):
        user = User.query.filter_by(name=username, email=email, student_id=student_id).first()
        if user:
            raise Exception("User already exists!")
        encryped_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(name=username, email=email, password=encryped_password, student_id=student_id)
        db.session.add(user)
        db.session.commit()
        auth_token = encode_auth_token(user.id)
        return RegisterUser(auth_token.decode())

class LogInUser(graphene.Mutation):
    """
    Logs in user
    """
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    auth_token = graphene.Field(graphene.String)

    def mutate(self, _, username, password):
        user = User.query.filter_by(name=username).first()
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
    Vaildates token
    """
    class Arguments:
        token = graphene.String(required=True)
        username = graphene.String(required=True)

    valid = graphene.Field(graphene.Boolean)

    def mutate(self, _, token, username):
        decoded_token_id = decode_auth_token(token)
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
    increment_item = IncrementItemQuantity.Field()
    check_out_item = CheckOutItem.Field()
    check_in_item = CheckInItem.Field()
    accept_checkout_request = AcceptCheckoutRequest.Field()
    show_transactions = ShowTransactions.Field()
    register_user = RegisterUser.Field()
    login_user = LogInUser.Field()
    validate_token = ValidateToken.Field()
