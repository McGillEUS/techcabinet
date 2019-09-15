from graphene.test import Client
import os
import pytest
import sys

sys.path.insert(0, os.getcwd())
from utils import db
from schema import schema, err_auth

client = Client(schema)
supersecret = 'secret'
email = 'potato@mail.com'
password = 'potato'


@pytest.fixture()
def clear_env():
    _environ = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(_environ)


@pytest.fixture()
def clear_db():
    db.session.commit()
    db.drop_all()
    db.create_all()
