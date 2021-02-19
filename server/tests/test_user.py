import json

from app.models import User

from .fixtures import client
from .functions import *


def test_new_user(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    rv = new_user(client, access_header, username="test")
    assert User.query.count() == 2
    rv = new_user(client, access_header)
    assert b"Missing username" in rv.data
    rv = new_user(client, access_header, username="")
    assert b"Invalid username (too long or empty)" in rv.data
    rv = new_user(client, access_header, username="test")
    assert b"This user already exists" in rv.data


def test_change_password(client):
    access_header, refresh_header = login_get_headers(client, "admin", "xss")
    rv = change_password(client, access_header)
    assert b"Missing data (password1, password2 or old_password)" in rv.data
    rv = change_password(client, access_header, old_password="xss", password1="a", password2="a")
    assert b"Password must be at least 8 characters and contain a uppercase letter, a lowercase letter and a number" in rv.data
    rv = change_password(client, access_header, old_password="xss", password1="Password123!", password2="Password122!")
    assert b"Passwords don't match" in rv.data
    rv = change_password(client, access_header, old_password="xss2", password1="Password123!", password2="Password123!")
    assert b"Old password is incorrect" in rv.data
    change_password(client, access_header, old_password="xss", password1="Password123!", password2="Password123!")
    logout(client, refresh_header)
    rv = login(client, {}, username="admin", password="Password123!", remember=False)
    assert rv._status_code == 200


def test_reset_password(client):
    access_header, refresh_header = login_get_headers(client, "admin", "xss")
    new_user(client, access_header, username="test")
    rv = reset_password(client, access_header, 2)
    password = json.loads(rv.data)["detail"]
    logout(client, refresh_header)
    rv = login(client, {}, username="test", password=password, remember=False)
    assert rv._status_code == 200


def test_get_user(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    rv = get_user(client, access_header)
    assert json.loads(rv.data)["username"] == "admin"


def test_delete_user(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    new_user(client, access_header, username="test")
    rv = delete_user(client, access_header, 1)
    assert b"Can't delete yourself" in rv.data
    rv = delete_user(client, access_header, 2)
    assert User.query.count() == 1
    rv = delete_user(client, access_header, 1)
    assert b"Can't delete the only user" in rv.data


def test_edit_user(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    new_user(client, access_header, username="test")
    rv = edit_user(client, access_header, 1, is_admin=0)
    assert b"Can't demote yourself" in rv.data
    rv = edit_user(client, access_header, 2)
    assert b"Missing data" in rv.data
    rv = edit_user(client, access_header, 2, is_admin=2)
    assert b"Invalid data" in rv.data
    rv = edit_user(client, access_header, 2, is_admin=1)
    assert b"modified successfuly" in rv.data


def test_get_users(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    rv = get_users(client, access_header)
    assert json.loads(rv.data)[0]["username"] == "admin"
