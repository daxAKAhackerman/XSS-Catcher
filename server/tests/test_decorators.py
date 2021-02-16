import json

from app.models import Client

from .fixtures import client
from .functions import *


def test_permissions(client):
    access_header, refresh_header = login_get_headers(client, "admin", "xss")
    rv = new_user(client, access_header, username="test")
    password = json.loads(rv.data)["detail"]
    create_client(client, access_header, name="name1", description="desc1")
    logout(client, refresh_header)
    access_header, _ = login_get_headers(client, "test", password)
    rv = new_user(client, access_header, username="test3")
    assert b"Only an administrator can do that" in rv.data
    rv = delete_client(client, access_header, 1)
    assert b"Insufficient permissions" in rv.data
    create_client(client, access_header, name="name2", description="desc1")
    client_name2 = Client.query.filter_by(id=2).first()
    get_x(client, access_header, "r", client_name2.uid)
    rv = delete_xss(client, access_header, 1)
    assert rv._status_code == 200
    rv = delete_client(client, access_header, 2)
    assert rv._status_code == 200
