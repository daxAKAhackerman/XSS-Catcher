import json
import time
from typing import Any, Optional

from app import db
from app.schemas import XSS, ApiKey, BlockedJti, Client, Settings, User
from flask.testing import FlaskClient


class Helpers:
    @staticmethod
    def login(client_tester: FlaskClient, username: str, password: str) -> tuple[str, str]:
        response = client_tester.post("/api/auth/login", json={"username": username, "password": password})

        if response_json := response.json:
            return response_json["access_token"], response_json["refresh_token"]
        else:
            raise Exception("Login helper response did not contain valid JSON")

    @staticmethod
    def create_client(name: str, owner_id: int = 1, webhook_url: Optional[str] = None, mail_to: Optional[str] = None, uid: Optional[str] = None) -> Client:
        client = Client(name=name, description="", owner_id=owner_id, webhook_url=webhook_url, mail_to=mail_to)
        if uid:
            client.uid = uid
        else:
            client.set_uid()
        db.session.add(client)
        db.session.commit()
        return client

    @staticmethod
    def create_user(username: str, password: str = "test") -> User:
        user = User(username=username, first_login=True, is_admin=False)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def delete_user(username: str) -> None:
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def set_settings(*args, **kwargs) -> Settings:
        current_settings = db.session.execute(db.select(Settings)).scalar_one()
        db.session.delete(current_settings)
        effective_settings = {"id": 1, "starttls": False, "ssl_tls": False, "webhook_type": 0, **kwargs}
        settings = Settings(**effective_settings)
        db.session.add(settings)
        db.session.commit()
        return settings

    @staticmethod
    def create_xss(
        headers: dict[str, str] = {}, ip_addr: str = "127.0.0.1", client_id: int = 1, xss_type: str = "stored", data: dict[str, Any] = {}, tags: list[str] = []
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

    @staticmethod
    def create_blocked_jti(jti: str) -> BlockedJti:
        blocked_jti = BlockedJti(jti=jti)
        db.session.add(blocked_jti)
        db.session.commit()
        return blocked_jti

    @staticmethod
    def create_api_key(key: Optional[str] = None, user_id: int = 1) -> ApiKey:
        api_key = ApiKey(key=key or ApiKey.generate_key(), owner_id=user_id)
        db.session.add(api_key)
        db.session.commit()
        return api_key
