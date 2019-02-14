from graphene.test import Client
import os
import pytest
import sys

from queries import create_user

sys.path.insert(0, os.getcwd())
from utils import db
from schema import schema, err_auth

client = Client(schema)
supersecret = 'secret'
username = 'potato'
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


@pytest.fixture()
def create_admin_account():
    os.environ['supersecretpassword'] = supersecret
    result = client.execute(create_user % (username+"_admin", password, 'email', 'studentid0', 'true', supersecret))
    return (username+"_admin", password, result['data']['registerUser']['authToken'])


@pytest.fixture()
def create_user_account():
    os.environ['supersecretpassword'] = supersecret
    result = client.execute(create_user % (username+"_regular", password, 'email', 'studentid1', 'false', supersecret))
    return (username+"_regular", password, result['data']['registerUser']['authToken'])
