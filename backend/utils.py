from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# app initialization
app = Flask(__name__)
app.debug = True


# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql:///techcabinetdata'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)
