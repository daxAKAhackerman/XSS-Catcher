import json
import random
import string
import uuid
from typing import Any, Optional

from app import db, jwt
from flask import Flask
from flask_sqlalchemy.model import Model
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

base_model = db._make_declarative_base(Model)


class Client(base_model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String(6), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    mail_to: Mapped[Optional[str]] = mapped_column(Text)
    webhook_url: Mapped[Optional[str]] = mapped_column(Text)

    xss: Mapped[list["XSS"]] = relationship("XSS", backref="client", lazy="dynamic")
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    def summary(self) -> dict[str, Any]:
        xss: list[XSS] = db.session.query(XSS).filter_by(client_id=self.id).all()
        loot_amount = 0
        for hit in xss:
            loot_amount += len(json.loads(hit.data or "{}"))
        data = {
            "owner_id": self.owner_id,
            "id": self.id,
            "name": self.name,
            "reflected": db.session.query(XSS).filter_by(client_id=self.id, xss_type="reflected").count(),
            "stored": db.session.query(XSS).filter_by(client_id=self.id, xss_type="stored").count(),
            "data": loot_amount,
        }
        return data

    def to_dict(self) -> dict[str, Any]:
        if self.owner_id is not None:
            owner_username = db.session.query(User).filter_by(id=self.owner_id).one().username
        else:
            owner_username = None
        data = {
            "owner": owner_username,
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

        while db.session.query(Client).filter_by(uid=uid).one_or_none() is not None:
            uid = "".join(random.choice(characters) for i in range(6))
        self.uid = uid


class XSS(base_model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip_addr: Mapped[str] = mapped_column(String(39), nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    xss_type: Mapped[str] = mapped_column(String(9), nullable=False)
    headers: Mapped[Optional[str]] = mapped_column(Text)
    data: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[str]] = mapped_column(Text)

    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("client.id"))

    def summary(self) -> dict[str, Any]:
        data = {"id": self.id, "ip_addr": self.ip_addr, "timestamp": self.timestamp, "tags": json.loads(self.tags or "[]")}
        return data

    def to_dict(self) -> dict[str, Any]:
        data = {
            "id": self.id,
            "headers": json.loads(self.headers or "{}"),
            "ip_addr": self.ip_addr,
            "data": json.loads(self.data or "{}"),
            "timestamp": self.timestamp,
            "tags": json.loads(self.tags or "[]"),
        }
        if "fingerprint" in data["data"].keys():
            data["data"]["fingerprint"] = ""
        if "dom" in data["data"].keys():
            data["data"]["dom"] = ""
        if "screenshot" in data["data"].keys():
            data["data"]["screenshot"] = ""

        return data


class ApiKey(base_model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)

    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    @staticmethod
    def generate_key() -> str:
        return str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "key": self.key}

    def to_obfuscated_dict(self) -> dict[str, Any]:
        return {"id": self.id, "key": len(self.key[:-8]) * "*" + self.key[-8:]}


class User(base_model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    first_login: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(32))

    client: Mapped[list[Client]] = relationship("Client", backref="owner", lazy="dynamic")
    api_key: Mapped[list[ApiKey]] = relationship("ApiKey", backref="owner", lazy="dynamic")

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


class Settings(base_model):
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


class BlockedJti(base_model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    jti: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)


@jwt.user_lookup_loader
def user_loader_callback(jwt_header: dict[str, Any], jwt_payload: dict[str, Any]) -> Optional[User]:
    return db.session.query(User).filter_by(username=jwt_payload["sub"]).one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header: dict[str, Any], jwt_payload: dict[str, Any]) -> bool:
    if jwt_payload["type"] == "access":
        return False
    else:
        blocked_jti = db.session.query(BlockedJti).filter_by(jti=jwt_payload["jti"]).one_or_none()
        return bool(blocked_jti)


def init_app(app: Flask) -> None:
    with app.app_context():
        if db.session.query(User).count() != 0:
            print("[-] User creation not needed")
        else:
            user = User(username="admin", is_admin=True, first_login=True)
            user.set_password("xss")
            db.session.add(user)
            db.session.commit()
            print("[+] Initial user created")

        if db.session.query(Settings).count() != 0:
            print("[-] Settings initialization not needed")
        else:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
            print("[+] Settings initialization successful")
        if db.session.query(BlockedJti).count() == 0:
            print("[-] JWT blocklist reset not needed")
        else:
            db.session.query(BlockedJti).delete()
            db.session.commit()
            print("[+] JWT blocklist reset successful")
