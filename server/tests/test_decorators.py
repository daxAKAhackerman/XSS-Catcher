import json

from app.models import Client

from .fixtures import client
from .functions import *


def test_permissions(client):
    login(client, username="admin", password="xss", remember=False)
    rv = new_user(client, username="test")
    password = json.loads(rv.data)["detail"]
    create_client(client, name="name1", description="desc1")
    logout(client)
    login(client, username="test", password=password, remember=False)
    rv = new_user(client, username="test3")
    assert b"Only an administrator can do that" in rv.data
    rv = delete_client(client, 1)
    assert b"Insufficient permissions" in rv.data
    create_client(client, name="name2", description="desc1")
    client_name2 = Client.query.filter_by(id=2).first()
    get_x(client, "r", client_name2.uid)
    rv = delete_xss(client, 1)
    assert rv._status_code == 200
    rv = delete_client(client, 2)
    assert rv._status_code == 200
