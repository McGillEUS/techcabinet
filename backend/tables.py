from utils import db


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    date_in = db.Column(db.DateTime)
    date_out = db.Column(db.DateTime)
    user_out = db.Column(db.String(256))
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return '<Item %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(256))
    date_created = db.Column(db.DateTime)

    def __repr__(self):
        return '<User %r>' % self.name
