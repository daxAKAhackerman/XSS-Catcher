import json

from app import db
from app.models import Blocklist, Client, Settings, User, init_app
from xss import app

from .fixtures import client, client_empty
from .functions import *


def test_client_to_dict_clients(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    client_name1 = Client.query.first()
    get_x(client, access_header, "r", client_name1.uid, test_data="test")
    rv = get_clients(client, access_header)
    assert json.loads(rv.data)[0]["data"] == 1


def test_client_to_dict_client(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    new_user(client, access_header, username="test")
    create_client(client, access_header, name="name1", description="desc1")
    edit_client(client, access_header, 1, owner=2)
    delete_user(client, access_header, id=2)
    rv = get_client(client, access_header, id=1)
    assert json.loads(rv.data)["owner"] == "Nobody"


def test_xss_to_dict(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    client_name1 = Client.query.first()
    post_x(
        client,
        access_header,
        "r",
        client_name1.uid,
        cookies="cookie=good",
        local_storage='{"local":"good"}',
        session_storage='{"session":"good"}',
        param="good",
        fingerprint='["good"]',
        dom="<br />",
        screenshot="O==",
    )
    rv = get_xss(client, access_header, 1)
    json_data = json.loads(rv.data)
    assert json_data["data"]["fingerprint"] == ""
    assert json_data["data"]["dom"] == ""
    assert json_data["data"]["screenshot"] == ""


def test_init_app_not_needed(client):
    get_user(client, {})
    init_app(app)
    assert Settings.query.count() == 1
    assert User.query.count() == 1
    assert Blocklist.query.count() == 0


def test_init_app_needed(client_empty):
    get_user(client_empty, {})
    init_app(app)
    assert Settings.query.count() == 1
    assert User.query.count() == 1
