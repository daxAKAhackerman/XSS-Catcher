import json

import pytest
from app.models import Settings
from app.utils import MissingDataError, send_mail

from .fixtures import client
from .functions import *

# Tests


def test_patch_settings(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    patch_settings(
        client, access_header, smtp_host="127.0.0.1", smtp_port=465, ssl_tls=True, mail_from="xsscatcher@hackerman.ca", smtp_user="admin", smtp_pass="admin"
    )
    settings = Settings.query.first()
    assert settings.smtp_host == "127.0.0.1"
    rv = patch_settings(client, access_header, smtp_host="{}.test.com".format("a" * 256), smtp_port=465)
    assert b"Server address too long" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port="a")
    assert b"Port is invalid" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=65536)
    assert b"Port is invalid" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1")
    assert b"Missing SMTP port" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=465, starttls=True, ssl_tls=True)
    assert b"Cannot use STARTTLS and SSL/TLS at the same time" in rv.data
    patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=587, starttls=True, mail_from="xsscatcher@hackerman.ca")
    settings = Settings.query.first()
    assert settings.starttls == True
    patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25, mail_from="xsscatcher@hackerman.ca")
    settings = Settings.query.first()
    assert settings.starttls == False and settings.ssl_tls == False
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25, mail_from="test")
    assert b"Email address format is invalid" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25)
    assert b"Missing sender address" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25, mail_from="xsscatcher@hackerman.ca", smtp_user="a" * 129, smtp_pass="admin")
    assert b"SMTP username too long" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25, mail_from="xsscatcher@hackerman.ca", smtp_user="admin", smtp_pass="a" * 129)
    assert b"SMTP password too long" in rv.data
    patch_settings(client, access_header, smtp_host="")
    settings = Settings.query.first()
    assert settings.smtp_port == None
    patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25, mail_from="xsscatcher@hackerman.ca")
    patch_settings(client, access_header)
    assert settings.smtp_port == None


def test_get_settings(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    rv = get_settings(client, access_header)
    assert json.loads(rv.data)["smtp_host"] == None


def test_send_mail(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25, mail_from="xsscatcher@hackerman.ca")
    rv = send_test_mail(client, access_header)
    assert b"Missing recipient" in rv.data
    rv = send_test_mail(client, access_header, mail_to="test")
    assert b"Invalid recipient" in rv.data
    rv = send_test_mail(client, access_header, mail_to="dax@hackerman.ca")
    assert b"Could not send test email" in rv.data
    patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=587, ssl_tls=True, mail_from="xsscatcher@hackerman.ca")
    rv = send_test_mail(client, access_header, mail_to="dax@hackerman.ca")
    assert b"Could not send test email" in rv.data
    with pytest.raises(MissingDataError):
        send_mail()
