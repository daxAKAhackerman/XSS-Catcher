import json

from fixtures import client
from tests.functions import *
from app.models import Client


def test_permissions(client):
    login(client, username='admin', password='xss', remember=False)
    rv = new_user(client, username='test')
    password = json.loads(rv.data)['detail']
    new_user(client, username='test2')
    create_client(client, name='name1', description='desc1')
    edit_client(client, 1, owner=3)
    client_name1 = Client.query.first()
    get_x(client, 'r', client_name1.uid)
    logout(client)
    login(client, username='test', password=password, remember=False)
    rv = new_user(client, username='test3')
    assert b'Only an administrator can do that' in rv.data

    rv = delete_client(client, 1)
    assert b'Insufficient permissions' in rv.data
