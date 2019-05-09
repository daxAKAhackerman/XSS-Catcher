from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import random
import string


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    guid = db.Column(db.CHAR(36), nullable=False)
    name = db.Column(db.String(32), unique=True, nullable=False)
    full_name = db.Column(db.String(128), unique=True)
    xss = db.relationship('XSS', backref='client', lazy='dynamic')

    def to_dict_clients(self):
        data = {
            'id': self.id,
            'name': self.name,
            'reflected': XSS.query.filter_by(client_id=self.id).filter_by(
                xss_type='reflected').count(),
            'stored': XSS.query.filter_by(client_id=self.id).filter_by(
                xss_type='stored').count(),
            'cookies': (XSS.query.filter_by(client_id=self.id).filter(XSS.cookies != None).count() + \
                        XSS.query.filter_by(client_id=self.id).filter(XSS.local_storage != None).count() + \
                        XSS.query.filter_by(client_id=self.id).filter(XSS.session_storage != None).count() + \
                        XSS.query.filter_by(client_id=self.id).filter(XSS.other_data != None).count())
        }
        return data

    def to_dict_client(self):
        data = {
            'id': self.id,
            'name': self.name,
            'guid': self.guid,
            'full_name': self.full_name
        }
        return data

    def gen_guid(self):

        new_guid = str(uuid.uuid4())

        while(Client.query.filter_by(guid=new_guid).first() != None):
            new_guid = str(uuid.uuid4())

        self.guid = new_guid


class XSS(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    referer = db.Column(db.String(256))
    user_agent = db.Column(db.String(128))
    ip_addr = db.Column(db.String(15))
    cookies = db.Column(db.TEXT)
    local_storage = db.Column(db.TEXT)
    session_storage = db.Column(db.TEXT)
    other_data = db.Column(db.TEXT)
    timestamp = db.Column(db.TEXT, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    xss_type = db.Column(db.String(9))

    def to_dict(self):
        data = {
            'id': self.id,
            'referer': self.referer,
            'user_agent': self.user_agent,
            'ip_addr': self.ip_addr,
            'cookies': self.cookies,
            'local_storage': self.local_storage,
            'session_storage': self.session_storage,
            'other_data': self.other_data,
            'timestamp': self.timestamp,
        }
        return data


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_login =db.Column(db.Boolean, nullable=False, default=1)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_password(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(12))


@login.user_loader
def load_user(id):
    return User.query.get(id)
