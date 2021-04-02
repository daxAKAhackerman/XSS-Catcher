import json

from app.models import Client

from .fixtures import client
from .functions import *

# Tests


def test_new_client(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    rv = create_client(client, access_header, name="test1")
    assert b"Missing name or description" in rv.data
    create_client(client, access_header, name="name1", description="desc1")
    client1 = Client.query.filter_by(id=1).first()
    assert client1.name == "name1"
    rv = create_client(client, access_header, name="name1", description="desc1")
    assert b"Client already exists" in rv.data
    rv = create_client(client, access_header, name="", description="desc1")
    assert b"Invalid data (name empty or too long or description too long)" in rv.data


def test_get_client(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    rv = get_client(client, access_header, 1)
    assert json.loads(rv.data)["name"] == "name1"


def test_edit_client(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    create_client(client, access_header, name="name3", description="desc3")
    edit_client(client, access_header, 1, name="name2", description="desc2", owner=1, mail_to="samdeg555@gmail.com", webhook_url="http://localhost/test")
    client1 = Client.query.filter_by(id=1).first()
    assert client1.name == "name2"
    assert client1.description == "desc2"
    rv = edit_client(client, access_header, 1, name="name3")
    assert b"Another client already uses this name" in rv.data
    rv = edit_client(client, access_header, 1, name="")
    assert b"Invalid name (too long or empty)" in rv.data
    rv = edit_client(client, access_header, 1, description="a" * 129)
    assert b"Invalid description (too long)"
    rv = edit_client(client, access_header, 1, owner=2)
    assert b"This user does not exist" in rv.data
    edit_client(client, access_header, 1, mail_to="")
    client1 = Client.query.filter_by(id=1).first()
    assert client1.mail_to is None
    rv = edit_client(client, access_header, 1, mail_to="abc")
    assert b"Invalid mail recipient" in rv.data
    rv = edit_client(client, access_header, 1, webhook_url="abc")
    assert b"Webhook URL format is invalid" in rv.data


def test_delete_client(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    assert Client.query.count() == 1
    delete_client(client, access_header, 1)
    assert Client.query.count() == 0


def test_get_clients(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    create_client(client, access_header, name="name2", description="desc2")
    rv = get_clients(client, access_header)
    assert len(json.loads(rv.data)) == 2
