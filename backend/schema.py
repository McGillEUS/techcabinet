from datetime import datetime
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from tables import Product, Cart, CartItem

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
    all_products = SQLAlchemyConnectionField(ProductObject)


class CreateItem(graphene.Mutation):
    """
    Creates an Item.
    Used for administrative and testing purposes, as users shall not
    be allowed to create products.

    Arguments:
    #TODO: Complete this
    name: Name of item.
    date_in:
    date_out:
    user_out:
    quantity:
    """
    class Arguments:
        name = graphene.String(required=True)
        #TODO: Complete        

    item = graphene.Field(lambda: ItemObject)

    def mutate(self, _, title, price, inventory_count):

        return CreateItem(item=item)


class Mutation(graphene.ObjectType):
    """
    Defines all available mutations.
    """
    create_item = CreateItem.Field()
