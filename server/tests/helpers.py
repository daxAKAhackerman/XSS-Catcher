import json
import time
from typing import Any, Dict, List

from app import db
from app.models import XSS, BlockedJti, Client, Settings, User
from flask.testing import FlaskClient


def login(client_tester: FlaskClient, username: str, password: str) -> tuple[str, str]:
    response = client_tester.post("/api/auth/login", json={"username": username, "password": password})
    return response.json["access_token"], response.json["refresh_token"]


def create_client(name: str, owner_id: int = 1, webhook_url: str = None, mail_to: str = None, uid: str = None) -> Client:
    client = Client(name=name, description="", owner_id=owner_id, webhook_url=webhook_url, mail_to=mail_to)
    if uid:
        client.uid = uid
    else:
        client.generate_uid()
    db.session.add(client)
    db.session.commit()
    return client


def create_user(username: str, password: str = "test") -> User:
    user = User(username=username, first_login=True, is_admin=False)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def set_settings(*args: List, **kwargs: Dict[str, Any]) -> Settings:
    current_settings = db.session.query(Settings).one()
    db.session.delete(current_settings)
    effective_settings = {"id": 1, "starttls": False, "ssl_tls": False, "webhook_type": 0, **kwargs}
    settings = Settings(**effective_settings)
    db.session.add(settings)
    db.session.commit()
    return settings


def create_xss(
    headers: Dict[str, str] = {}, ip_addr: str = "127.0.0.1", client_id: int = 1, xss_type: str = "stored", data: Dict[str, Any] = {}, tags: List[str] = []
) -> XSS:
    xss = XSS(
        headers=json.dumps(headers),
        ip_addr=ip_addr,
        client_id=client_id,
        xss_type=xss_type,
        data=json.dumps(data),
        timestamp=int(time.time()),
        tags=json.dumps(tags),
    )
    db.session.add(xss)
    db.session.commit()
    return xss


def create_blocked_jti(jti: str) -> BlockedJti:
    blocked_jti = BlockedJti(jti=jti)
    db.session.add(blocked_jti)
    db.session.commit()
    return blocked_jti
