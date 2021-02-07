import json

from app.models import XSS, Client, Settings

from .fixtures import client
from .functions import *

# Tests


def test_new_xss(client):
    login(client, username="admin", password="xss", remember=True)
    create_client(client, name="TEST_NAME", description="Test description")
    client_obj = Client.query.filter_by(id=1).first()
    post_x(
        client,
        "r",
        client_obj.uid,
        cookies="cookie=good",
        local_storage='{"local":"good"}',
        session_storage='{"session":"good"}',
        param="good",
        fingerprint='["good"]',
        dom="<br />",
    )
    get_x(client, "s", client_obj.uid, headers={"X-Forwarded-For": "127.0.0.2"})
    xss1 = XSS.query.filter_by(id=1).first()
    xss2 = XSS.query.filter_by(id=2).first()
    xss1_json = json.loads(xss1.data)
    xss2_json = json.loads(xss2.data)
    assert xss1_json["cookies"][0] == {"cookie": "good"}
    assert xss1_json["local_storage"][0] == {"local": "good"}
    assert xss1_json["session_storage"][0] == {"session": "good"}
    assert xss1_json["param"] == "good"
    assert xss1_json["fingerprint"] == '["good"]'
    assert xss1_json["dom"] == "<html>\n<br />\n</html>"
    assert xss1.xss_type == "reflected"
    assert xss1.ip_addr == "127.0.0.1"
    for header in json.loads(xss1.headers):
        if "User-Agent" in header.keys():
            assert "werkzeug" in header["User-Agent"]
    int(xss1.timestamp)
    assert xss2.xss_type == "stored"
    assert xss2.ip_addr == "127.0.0.2"
    rv = get_x(client, "r", "AAAAA")
    assert rv._status_code == 200
    assert XSS.query.count() == 2
    patch_settings(client, smtp_host="127.0.0.1", smtp_port=25, mail_from="xsscatcher@hackerman.ca")
    edit_client(client, 1, mail_to="dax@hackerman.ca")
    get_x(client, "s", client_obj.uid)
    settings = Settings.query.first()
    assert settings.smtp_status == False
