import hashlib
import json
import random
import string
import uuid
from typing import Dict, List

from app import db, jwt
from flask import Flask
from sqlalchemy.sql import expression
from werkzeug.security import check_password_hash, generate_password_hash


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    uid = db.Column(db.String(6), unique=True, nullable=False)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(128))
    mail_to = db.Column(db.Text)
    webhook_url = db.Column(db.Text)
    xss = db.relationship("XSS", backref="client", lazy="dynamic")
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def summary(self):
        loot_amount = 0
        xss: List[XSS] = db.session.query(XSS).filter_by(client_id=self.id).all()
        for hit in xss:
            loot_amount += len(json.loads(hit.data))
        data = {
            "owner_id": self.owner_id,
            "id": self.id,
            "name": self.name,
            "reflected": db.session.query(XSS).filter_by(client_id=self.id, xss_type="reflected").count(),
            "stored": db.session.query(XSS).filter_by(client_id=self.id, xss_type="stored").count(),
            "data": loot_amount,
        }
        return data

    def to_dict(self):
        if self.owner_id is not None:
            owner_username = db.session.query(User).filter_by(id=self.owner_id).one().username
        else:
            owner_username = "nobody"
        data = {
            "owner": owner_username,
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "mail_to": self.mail_to,
            "webhook_url": self.webhook_url,
        }
        return data

    def generate_uid(self):
        characters = string.ascii_letters + string.digits
        uid = "".join(random.choice(characters) for i in range(6))

        while db.session.query(Client).filter_by(uid=uid).one_or_none() is not None:
            uid = "".join(random.choice(characters) for i in range(6))
        self.uid = uid


class XSS(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    headers = db.Column(db.Text, nullable=False)
    ip_addr = db.Column(db.String(39), nullable=False)
    data = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    xss_type = db.Column(db.String(9))
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))

    def to_dict(self):
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

    def summary(self):
        data = {"id": self.id, "ip_addr": self.ip_addr, "timestamp": self.timestamp, "tags": json.loads(self.tags)}
        return data


class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    key = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @staticmethod
    def generate_key():
        return str(uuid.uuid4())

    def to_dict(self):
        return {"id": self.id, "key": self.key}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    first_login = db.Column(db.Boolean, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    mfa_secret = db.Column(db.String(32))
    client = db.relationship("Client", backref="owner", lazy="dynamic")
    api_key = db.relationship("ApiKey", backref="owner", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_password():
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for i in range(12))

    def to_dict(self):
        data = {"id": self.id, "username": self.username, "first_login": self.first_login, "is_admin": self.is_admin, "mfa": bool(self.mfa_secret)}
        return data


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    smtp_host = db.Column(db.String(256))
    smtp_port = db.Column(db.Integer)
    starttls = db.Column(db.Boolean, nullable=False)
    ssl_tls = db.Column(db.Boolean, nullable=False)
    mail_from = db.Column(db.Text)
    smtp_user = db.Column(db.String(128))
    smtp_pass = db.Column(db.String(128))
    smtp_status = db.Column(db.Boolean)
    mail_to = db.Column(db.Text)
    webhook_url = db.Column(db.Text)
    webhook_type = db.Column(db.Integer, nullable=False)

    def to_dict(self):
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
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    jti = db.Column(db.String(64), nullable=False, unique=True)


@jwt.user_lookup_loader
def user_loader_callback(jwt_header: Dict, jwt_payload: Dict) -> User:
    return db.session.query(User).filter_by(username=jwt_payload["sub"]).one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header: Dict, jwt_payload: Dict) -> bool:
    if jwt_payload["type"] == "access":
        return False
    else:
        blocked_jti: BlockedJti = db.session.query(BlockedJti).filter_by(jti=jwt_payload["jti"]).one_or_none()
        return bool(blocked_jti)


def init_app(app: Flask):
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
            settings = Settings(starttls=False, ssl_tls=False, webhook_type=0)
            db.session.add(settings)
            db.session.commit()
            print("[+] Settings initialization successful")
        if db.session.query(BlockedJti).count() == 0:
            print("[-] JWT blocklist reset not needed")
        else:
            db.session.query(BlockedJti).delete()
            db.session.commit()
            print("[+] JWT blocklist reset successful")
