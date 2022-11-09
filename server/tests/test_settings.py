from flask.testing import FlaskClient
from tests.helpers import login


def test__settings_get__given_request__then_settings_returned(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get("/api/settings", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {
        "mail_from": None,
        "mail_to": None,
        "smtp_host": None,
        "smtp_port": None,
        "smtp_status": None,
        "smtp_user": None,
        "ssl_tls": False,
        "starttls": False,
        "webhook_url": None,
    }
    assert response.status_code == 200
