from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


"""
Utils related to the app setup
"""
# app initialization
app = Flask(__name__)
app.debug = True


# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql:///techcabinetdata'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "")

db = SQLAlchemy(app)

token_expiry =  int(os.environ.get("TOKEN_EXPIRY", "180"))
