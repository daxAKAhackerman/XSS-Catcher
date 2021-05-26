import json
import random
import string

from app import db, jwt
from werkzeug.security import check_password_hash, generate_password_hash


class Client(db.Model):
    """Defines a client"""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    uid = db.Column(db.String(6), unique=True, nullable=False)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(128))
    mail_to = db.Column(db.String(256), nullable=True)
    webhook_url = db.Column(db.Text, nullable=True)
    xss = db.relationship("XSS", backref="client", lazy="dynamic")
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def to_dict_clients(self):
        """Returns a dict containing client's data to be displayed in a list of clients"""
        data_num = 0
        xss = XSS.query.filter_by(client_id=self.id).all()
        for hit in xss:
            data_num += len(json.loads(hit.data))
        data = {
            "owner_id": self.owner_id,
            "id": self.id,
            "name": self.name,
            "reflected": XSS.query.filter_by(client_id=self.id).filter_by(xss_type="reflected").count(),
            "stored": XSS.query.filter_by(client_id=self.id).filter_by(xss_type="stored").count(),
            "data": data_num,
        }
        return data

    def to_dict_client(self):
        """Returns a dict containing client's data"""
        owner = None
        if self.owner_id != None:
            owner = User.query.filter_by(id=self.owner_id).first().username
        if owner == None:
            owner = "Nobody"
        data = {"owner": owner, "id": self.id, "name": self.name, "description": self.description, "mail_to": self.mail_to, "webhook_url": self.webhook_url}
        return data

    def gen_uid(self):
        """Generates a UID"""
        characters = string.ascii_letters + string.digits
        new_uid = "".join(random.choice(characters) for i in range(6))

        while Client.query.filter_by(uid=new_uid).first() != None:
            new_uid = "".join(random.choice(characters) for i in range(6))
        self.uid = new_uid


class XSS(db.Model):
    """Defines an XSS"""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    headers = db.Column(db.Text)
    ip_addr = db.Column(db.String(15))
    data = db.Column(db.Text)
    tags = db.Column(db.Text, server_default="[]", nullable=False)
    timestamp = db.Column(db.Integer)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    xss_type = db.Column(db.String(9))

    def to_dict(self):
        """Returns full representation of XSS"""
        data = {
            "id": self.id,
            "headers": json.loads(self.headers),
            "ip_addr": self.ip_addr,
            "data": json.loads(self.data) if self.data != None else self.data,
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

    def to_dict_short(self):
        """Returns an abridged representation of XSS"""
        data = {"id": self.id, "ip_addr": self.ip_addr, "timestamp": self.timestamp, "tags": json.loads(self.tags)}
        return data


class User(db.Model):
    """Defines a user"""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    first_login = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    client = db.relationship("Client", backref="owner", lazy="dynamic")

    def set_password(self, password):
        """Sets user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Validates user's password"""
        return check_password_hash(self.password_hash, password)

    def generate_password(self):
        """Generates a new password"""
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for i in range(12))

    def to_dict(self):
        """Returns a representation of the user"""
        data = {"id": self.id, "username": self.username, "first_login": self.first_login, "is_admin": self.is_admin}
        return data


class Settings(db.Model):
    """Holds app settings"""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    smtp_host = db.Column(db.String(256), nullable=True)
    smtp_port = db.Column(db.Integer, nullable=True)
    starttls = db.Column(db.Boolean, default=False, nullable=True)
    ssl_tls = db.Column(db.Boolean, default=False, nullable=True)
    mail_from = db.Column(db.String(256), nullable=True)
    smtp_user = db.Column(db.String(128), nullable=True)
    smtp_pass = db.Column(db.String(128), nullable=True)
    smtp_status = db.Column(db.Boolean, nullable=True)
    mail_to = db.Column(db.Text, nullable=True)
    webhook_url = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """Returns the settings"""
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
        }
        return data


class Blocklist(db.Model):
    "Holds blocked refresh token jti"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    jti = db.Column(db.String(64), nullable=False, unique=True)


@jwt.user_lookup_loader
def user_loader_callback(_, jwt_payload):
    return User.query.filter_by(username=jwt_payload["sub"]).first()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(_, jwt_payload):
    if jwt_payload["type"] == "access":
        return False
    else:
        blocked_jti = Blocklist.query.filter_by(jti=jwt_payload["jti"]).first()
        return True if blocked_jti else False


def init_app(app):
    """Creates the admin user and the settings"""
    with app.app_context():
        if db.session.query(User).count() != 0:
            print("[-] User creation not needed")
        else:
            user = User(username="admin", is_admin=1)
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
        if db.session.query(Blocklist).count() == 0:
            print("[-] JWT blocklist reset not needed")
        else:
            db.session.query(Blocklist).delete()
            db.session.commit()
            print("[+] JWT blocklist reset successful")
