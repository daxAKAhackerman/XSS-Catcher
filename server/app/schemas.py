import json
import random
import string
import uuid
from typing import Any, Optional

from app import db, jwt
from flask import Flask
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash


class Client(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String(6), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    mail_to: Mapped[Optional[str]] = mapped_column(Text)
    webhook_url: Mapped[Optional[str]] = mapped_column(Text)

    xss: Mapped[list["XSS"]] = relationship("XSS", backref="client", lazy="dynamic")
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("user.id"))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def summary(self) -> dict[str, Any]:
        xss: list[XSS] = list(db.session.execute(db.select(XSS).filter_by(client_id=self.id)).scalars().all())
        loot_amount = 0
        for hit in xss:
            loot_amount += len(json.loads(hit.data))
        data = {
            "owner_id": self.owner_id,
            "id": self.id,
            "name": self.name,
            "reflected": db.session.execute(
                db.select(db.func.count()).select_from(XSS).where(XSS.client_id == self.id).where(XSS.xss_type == "reflected")
            ).scalar(),
            "stored": db.session.execute(db.select(db.func.count()).select_from(XSS).where(XSS.client_id == self.id).where(XSS.xss_type == "stored")).scalar(),
            "data": loot_amount,
        }
        return data

    def to_dict(self) -> dict[str, Any]:
        data = {
            "owner_id": self.owner_id,
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "mail_to": self.mail_to,
            "webhook_url": self.webhook_url,
        }
        return data

    def set_uid(self) -> None:
        characters = string.ascii_letters + string.digits
        uid = "".join(random.choice(characters) for i in range(6))

        while db.session.execute(db.select(Client).filter_by(uid=uid)).scalar_one_or_none() is not None:
            uid = "".join(random.choice(characters) for i in range(6))
        self.uid = uid


class XSS(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip_addr: Mapped[str] = mapped_column(String(39), nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    xss_type: Mapped[str] = mapped_column(String(9), nullable=False)
    headers: Mapped[str] = mapped_column(Text)
    data: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(Text)

    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("client.id"))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def summary(self) -> dict[str, Any]:
        data = {"id": self.id, "ip_addr": self.ip_addr, "timestamp": self.timestamp, "tags": json.loads(self.tags)}
        return data

    def to_dict(self) -> dict[str, Any]:
        data = {
            "id": self.id,
            "headers": json.loads(self.headers),
            "ip_addr": self.ip_addr,
            "data": json.loads(self.data),
            "timestamp": self.timestamp,
            "tags": json.loads(self.tags),
        }
        if "fingerprint" in data["data"].keys():
            data["data"]["fingerprint"] = ""
        if "dom" in data["data"].keys():
            data["data"]["dom"] = ""
        if "screenshot" in data["data"].keys():
            data["data"]["screenshot"] = ""

        return data


class ApiKey(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)

    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @staticmethod
    def generate_key() -> str:
        return str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "key": self.key}

    def to_obfuscated_dict(self) -> dict[str, Any]:
        return {"id": self.id, "key": len(self.key[:-8]) * "*" + self.key[-8:]}


class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    first_login: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(32))

    client: Mapped[list[Client]] = relationship("Client", backref="owner", lazy="dynamic")
    api_key: Mapped[list[ApiKey]] = relationship("ApiKey", backref="owner", lazy="dynamic")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @staticmethod
    def generate_password() -> str:
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for i in range(12))

    def to_dict(self) -> dict[str, Any]:
        data = {"id": self.id, "username": self.username, "first_login": self.first_login, "is_admin": self.is_admin, "mfa": bool(self.mfa_secret)}
        return data

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Settings(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    smtp_host: Mapped[Optional[str]] = mapped_column(Text)
    smtp_port: Mapped[Optional[int]] = mapped_column(Integer)
    starttls: Mapped[Optional[bool]] = mapped_column(Boolean)
    ssl_tls: Mapped[Optional[bool]] = mapped_column(Boolean)
    mail_from: Mapped[Optional[str]] = mapped_column(Text)
    smtp_user: Mapped[Optional[str]] = mapped_column(Text)
    smtp_pass: Mapped[Optional[str]] = mapped_column(Text)
    smtp_status: Mapped[Optional[bool]] = mapped_column(Boolean)
    mail_to: Mapped[Optional[str]] = mapped_column(Text)
    webhook_url: Mapped[Optional[str]] = mapped_column(Text)
    webhook_type: Mapped[Optional[int]] = mapped_column(Integer)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "starttls": self.starttls,
            "ssl_tls": self.ssl_tls,
            "mail_from": self.mail_from,
            "mail_to": self.mail_to,
            "smtp_user": self.smtp_user,
            "smtp_status": self.smtp_status,
            "webhook_url": self.webhook_url,
            "webhook_type": self.webhook_type,
        }
        return data


class BlockedJti(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    jti: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


@jwt.user_lookup_loader
def user_loader_callback(jwt_header: dict[str, Any], jwt_payload: dict[str, Any]) -> Optional[User]:
    return db.session.execute(db.select(User).filter_by(username=jwt_payload["sub"])).scalar_one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header: dict[str, Any], jwt_payload: dict[str, Any]) -> bool:
    if jwt_payload["type"] == "access":
        return False
    else:
        blocked_jti = db.session.execute(db.select(BlockedJti).filter_by(jti=jwt_payload["jti"])).scalar_one_or_none()
        return bool(blocked_jti)


def init_app(app: Flask) -> None:
    with app.app_context():
        user_count = db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
        if user_count is not None and user_count != 0:
            print("[-] User creation not needed")
        else:
            user = User(username="admin", is_admin=True, first_login=True)
            user.set_password("xss")
            db.session.add(user)
            db.session.commit()
            print("[+] Initial user created")

        settings_count = db.session.execute(db.select(db.func.count()).select_from(Settings)).scalar()
        if settings_count is not None and settings_count != 0:
            print("[-] Settings initialization not needed")
        else:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
            print("[+] Settings initialization successful")
        if db.session.execute(db.select(db.func.count()).select_from(BlockedJti)).scalar() == 0:
            print("[-] JWT blocklist reset not needed")
        else:
            db.session.execute(db.delete(BlockedJti))
            db.session.commit()
            print("[+] JWT blocklist reset successful")
