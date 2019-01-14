from datetime import datetime
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from tables import Item

from utils import db


class ItemObject(SQLAlchemyObjectType):
    """
    Maps to `Item` table in Database.
    """
    class Meta:
        model = Item
        interfaces = (graphene.relay.Node, )


class UserObject(SQLAlchemyObjectType):
    """
    Maps to `User` table in Database.
    """
    class Meta:
        model = Item
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

    item = graphene.Field(lambda: ItemObject)

    def mutate(self, _, name, quantity):
        item = Item(name=name, quantity=quantity, date_in=datetime.now())
        db.session.add(item)
        db.session.commit()
        return CreateItem(item=item)


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
        return DeleteItem(items=items)


class ShowItems(graphene.Mutation):
    """
    Shows all items in the database
    """
    items = graphene.List(ItemObject)

    def mutate(self, _):
        items = Item.query.all()
        return ShowItems(items=items)

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
        quantity = graphene.Int(required=True)
        checked_out_by = graphene.String(required=True)

    items = graphene.List(ItemObject)

    def mutate(self, _, name, quantity, checked_out_by):
        if quantity < 0:
            raise Exception("Positive quantities only.")

        item = Item.query.filter_by(name=name).first()
        if item.quantity - quantity < 0:
            raise Exception("Item not available.")
        item.quantity -= quantity
        item.user_out = checked_out_by
        item.date_out = datetime.now()
        items = Item.query.all()
        return CheckOutItem(items)

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