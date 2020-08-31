import os
import pytest

from xss import app
from shutil import copyfile


@pytest.fixture
def client():

    basedir = os.path.abspath(os.path.dirname(__file__))

    copyfile(os.path.join(basedir, 'app_test.db.template'),
             os.path.join(basedir, 'app_test.db'))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(basedir, 'app_test.db')
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

    os.remove(os.path.join(basedir, 'app_test.db'))


@pytest.fixture
def client_empty():

    basedir = os.path.abspath(os.path.dirname(__file__))

    copyfile(os.path.join(basedir, 'app_test_empty.db.template'),
             os.path.join(basedir, 'app_test.db'))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(basedir, 'app_test.db')
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

    os.remove(os.path.join(basedir, 'app_test.db'))
