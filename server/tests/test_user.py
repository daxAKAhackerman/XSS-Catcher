from fixtures import client
from tests.functions import *
from app.models import User

import json


def test_new_user(client):
    login(client, username='admin', password='xss', remember=False)
    rv = new_user(client, username='test')
    assert User.query.count() == 2
    rv = new_user(client)
    assert b'Missing username' in rv.data
    rv = new_user(client, username='')
    assert b'Invalid username (too long or empty)' in rv.data
    rv = new_user(client, username='test')
    assert b'This user already exists' in rv.data


def test_change_password(client):
    login(client, username='admin', password='xss', remember=False)
    rv = change_password(client)
    assert b'Missing data (password1, password2 or old_password)' in rv.data
    rv = change_password(client, old_password='xss',
                         password1='a', password2='a')
    assert b'Password must be at least 8 characters and contain a uppercase letter, a lowercase letter and a number' in rv.data
    rv = change_password(client, old_password='xss',
                         password1='Password123!', password2='Password122!')
    assert b'Passwords don\'t match' in rv.data
    rv = change_password(client, old_password='xss2',
                         password1='Password123!', password2='Password123!')
    assert b'Old password is incorrect' in rv.data
    change_password(client, old_password='xss',
                    password1='Password123!', password2='Password123!')
    logout(client)
    rv = login(client, username='admin',
               password='Password123!', remember=False)
    assert rv._status_code == 200


def test_reset_password(client):
    login(client, username='admin', password='xss', remember=False)
    new_user(client, username='test')
    rv = reset_password(client, 2)
    password = json.loads(rv.data)['detail']
    logout(client)
    rv = login(client, username='test', password=password, remember=False)
    assert rv._status_code == 200


def test_get_user(client):
    login(client, username='admin', password='xss', remember=False)
    rv = get_user(client)
    print(rv.data)
    assert json.loads(rv.data)['username'] == 'admin'


def test_delete_user(client):
    login(client, username='admin', password='xss', remember=False)
    new_user(client, username='test')
    rv = delete_user(client, 1)
    assert b'Can\'t delete yourself' in rv.data
    rv = delete_user(client, 2)
    assert User.query.count() == 1
    rv = delete_user(client, 1)
    assert b'Can\'t delete the only user' in rv.data


def test_edit_user(client):
    login(client, username='admin', password='xss', remember=False)
    new_user(client, username='test')
    rv = edit_user(client, 1, is_admin=0)
    assert b'Can\'t demote yourself' in rv.data
    rv = edit_user(client, 2)
    assert b'Missing data' in rv.data
    rv = edit_user(client, 2, is_admin=2)
    assert b'Invalid data' in rv.data
    rv = edit_user(client, 2, is_admin=1)
    assert b'modified successfuly' in rv.data


def test_get_users(client):
    login(client, username='admin', password='xss', remember=False)
    rv = get_users(client)
    print(rv.data)
    assert json.loads(rv.data)[0]['username'] == 'admin'
