import json

from app.models import XSS, Client, Settings

from .fixtures import client
from .functions import *

# Tests


def test_new_xss(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    create_client(client, access_header, name="TEST_NAME", description="Test description")
    client_obj = Client.query.filter_by(id=1).first()
    post_x(
        client,
        {},
        "r",
        client_obj.uid,
        tags="tag1,tag2",
        cookies="cookie=good",
        local_storage='{"local":"good"}',
        session_storage='{"session":"good"}',
        param="good",
        fingerprint='["good"]',
        dom="<br />",
    )
    get_x(client, {"X-Forwarded-For": "127.0.0.2"}, "s", client_obj.uid)
    post_x_form(client, {}, "s", client_obj.uid, cookies="cookie=good")
    xss1 = XSS.query.filter_by(id=1).first()
    xss2 = XSS.query.filter_by(id=2).first()
    xss3 = XSS.query.filter_by(id=3).first()
    xss1_json = json.loads(xss1.data)
    assert xss1_json["cookies"] == {"cookie": "good"}
    assert xss1_json["local_storage"] == {"local": "good"}
    assert xss1_json["session_storage"] == {"session": "good"}
    assert xss1_json["param"] == "good"
    assert xss1_json["fingerprint"] == '["good"]'
    assert xss1_json["dom"] == "<html>\n<br />\n</html>"
    assert xss1.xss_type == "reflected"
    assert xss1.ip_addr == "127.0.0.1"
    assert xss1.tags == '["tag1", "tag2"]'
    assert "werkzeug" in json.loads(xss1.headers)["User-Agent"]
    int(xss1.timestamp)
    assert xss2.xss_type == "stored"
    assert xss2.ip_addr == "127.0.0.2"
    xss3_json = json.loads(xss3.data)
    assert xss3_json["cookies"] == {"cookie": "good"}
    rv = get_x(client, access_header, "r", "AAAAA")
    assert rv._status_code == 200
    assert XSS.query.count() == 3
    patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25, mail_from="xsscatcher@hackerman.ca")
    edit_client(client, access_header, 1, mail_to="dax@hackerman.ca")
    get_x(client, access_header, "s", client_obj.uid)
    settings = Settings.query.first()
    assert settings.smtp_status == False
