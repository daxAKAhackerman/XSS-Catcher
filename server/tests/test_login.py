from fixtures import client
from tests.functions import *

import json


# Tests

def test_login(client):

    rv = login(client, username='admin', password='xss', remember=True)
    assert b'OK' in rv.data

    login(client, username='admin', password='xss', remember=True)

    rv = login(client, username='admin', password='xss', remember=True)
    assert b'Already logged in' in rv.data

    logout(client)

    rv = login(client, username='admin', remember=True)
    assert b'Missing username or password' in rv.data

    rv = login(client, username='admin', password='xss')
    assert b'OK' in rv.data

    logout(client)

    rv = login(client, username='bad_username',
               password='bad_password', remember=True)
    assert b'Bad username or password' in rv.data


def test_logout(client):

    login(client, username='admin', password='xss', remember=True)
    rv = logout(client)
    raise_logout = False

    for k, v in rv.headers:
        if (k == 'Set-Cookie') and ('session=;' in v):
            raise_logout = True

    assert raise_logout
