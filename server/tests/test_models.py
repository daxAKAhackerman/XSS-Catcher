import json

from app import db
from app.models import Client, Settings, User, init_app
from xss import app

from .fixtures import client, client_empty
from .functions import *


def test_client_to_dict_clients(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    client_name1 = Client.query.first()
    get_x(client, "r", client_name1.uid, test_data="test")
    rv = get_clients(client)
    assert json.loads(rv.data)[0]["data"] == 1


def test_client_to_dict_client(client):
    login(client, username="admin", password="xss", remember=False)
    new_user(client, username="test")
    create_client(client, name="name1", description="desc1")
    edit_client(client, 1, owner=2)
    delete_user(client, id=2)
    rv = get_client(client, id=1)
    assert json.loads(rv.data)["owner"] == "Nobody"


def test_xss_to_dict(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    client_name1 = Client.query.first()
    post_x(
        client,
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
    rv = get_xss(client, 1)
    json_data = json.loads(rv.data)
    print(json_data)
    assert json_data["data"]["fingerprint"] == ""
    assert json_data["data"]["dom"] == ""
    assert json_data["data"]["screenshot"] == ""


def test_init_app_not_needed(client):
    get_user(client)
    init_app(app)
    assert Settings.query.count() == 1
    assert User.query.count() == 1


def test_init_app_needed(client_empty):
    get_user(client_empty)
    init_app(app)
    assert Settings.query.count() == 1
    assert User.query.count() == 1
