from utils import db


class Item(db.Model):
    __tablename__ = 'items'

    name = db.Column(db.String(256), primary_key=True)
    created_by = db.Column(db.String(256), db.ForeignKey('admins.email'))
    date_in = db.Column(db.DateTime)
    date_out = db.Column(db.DateTime)
    quantity = db.Column(db.Integer)

    transactions = db.relationship("Transaction", backref="items", lazy=True)

    def __repr__(self):
        return '<Item %r>' % self.name


class Admin(db.Model):
    __tablename__ = 'admins'

    email = db.Column(db.String(256), primary_key=True)
    name = db.Column(db.String(256))
    date_created = db.Column(db.DateTime)

    items = db.relationship("Item", backref="admins", lazy=True)

    def __repr__(self):
        return '<Admin %r>' % self.name


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_requested_id = db.Column(db.String(256))
    user_requested_email = db.Column(db.String(256))
    admin_accepted = db.Column(db.String(256))
    requested_quantity = db.Column(db.Integer)
    accepted = db.Column(db.Boolean)
    returned = db.Column(db.Boolean)
    item = db.Column(db.String(256), db.ForeignKey('items.name'))
    date_requested = db.Column(db.DateTime)
    date_accepted = db.Column(db.DateTime)
    date_returned = db.Column(db.DateTime)

    def __repr__(self):
        return '<Transaction %r>' % self.id
