import json

from app.models import Client

from .fixtures import client
from .functions import *

# Tests


def test_new_client(client):
    login(client, username="admin", password="xss", remember=False)
    rv = create_client(client, name="test1")
    assert b"Missing name or description" in rv.data
    create_client(client, name="name1", description="desc1")
    client1 = Client.query.filter_by(id=1).first()
    assert client1.name == "name1"
    rv = create_client(client, name="name1", description="desc1")
    assert b"Client already exists" in rv.data
    rv = create_client(client, name="", description="desc1")
    assert b"Invalid data (name empty or too long or description too long)" in rv.data


def test_get_client(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    rv = get_client(client, 1)
    assert json.loads(rv.data)["name"] == "name1"


def test_edit_client(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    create_client(client, name="name3", description="desc3")
    edit_client(client, 1, name="name2", description="desc2", owner=1, mail_to="samdeg555@gmail.com")
    client1 = Client.query.filter_by(id=1).first()
    assert client1.name == "name2"
    assert client1.description == "desc2"
    rv = edit_client(client, 1, name="name3")
    assert b"Another client already uses this name" in rv.data
    rv = edit_client(client, 1, name="")
    assert b"Invalid name (too long or empty)" in rv.data
    rv = edit_client(client, 1, description="a" * 129)
    assert b"Invalid description (too long)"
    rv = edit_client(client, 1, owner=2)
    assert b"This user does not exist" in rv.data
    edit_client(client, 1, mail_to="")
    client1 = Client.query.filter_by(id=1).first()
    assert client1.mail_to is None
    rv = edit_client(client, 1, mail_to="abc")
    assert b"Invalid mail recipient" in rv.data


def test_delete_client(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    assert Client.query.count() == 1
    rv = delete_client(client, 1)
    assert Client.query.count() == 0


def test_get_xss_all(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    client1 = Client.query.filter_by(id=1).first()
    get_x(client, "r", client1.uid)
    rv = get_xss_all(client, 1, "reflected")
    assert len(json.loads(rv.data)) == 1
    rv = get_xss_all(client, 1, "badtype")
    assert b"Unknown XSS type" in rv.data


def test_get_single_xss(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    client1 = Client.query.filter_by(id=1).first()
    get_x(client, "r", client1.uid)
    rv = get_single_xss(client, 1, 1)
    assert "ip_addr" in json.loads(rv.data).keys()


def test_get_loot(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    client1 = Client.query.filter_by(id=1).first()
    get_x(client, "r", client1.uid, test_data="test", dom="<h1>test</h1>")
    rv = get_loot(client, 1)
    assert json.loads(rv.data)["test_data"][0]["1"] == "test"
    assert json.loads(rv.data)["dom"][0]["1"] == ""


def test_get_clients(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    create_client(client, name="name2", description="desc2")
    rv = get_clients(client)
    assert len(json.loads(rv.data)) == 2
