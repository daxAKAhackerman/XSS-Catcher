import json

from .fixtures import client
from .functions import *

# Tests


def test_login(client):
    rv = login(client, {}, username="admin", password="xss")
    assert b"OK" in rv.data
    access_header, refresh_header = login_get_headers(client, "admin", "xss")
    rv = login(client, access_header, username="admin", password="xss")
    assert b"Already logged in" in rv.data
    logout(client, refresh_header)
    rv = login(client, {}, username="admin")
    assert b"Missing username or password" in rv.data
    rv = login(client, {}, username="bad_username", password="bad_password")
    assert b"Bad username or password" in rv.data


def test_logout(client):
    access_header, refresh_header = login_get_headers(client, "admin", "xss")
    print(access_header)
    print(refresh_header)
    rv = logout(client, refresh_header)
    assert b"Logged out successfully" in rv.data


def test_refresh(client):
    _, refresh_header = login_get_headers(client, "admin", "xss")
    rv = refresh(client, refresh_header)
    assert b"access_token" in rv.data
