from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import json


class Client(db.Model):
    """Defines a client"""
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    uid = db.Column(db.String(6), unique=True, nullable=False)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(128))
    xss = db.relationship('XSS', backref='client', lazy='dynamic')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict_clients(self):
        """Returns a dict containing client's data to be displayed in a list of clients"""
        data_num = 0
        xss = XSS.query.filter_by(client_id=self.id).all()
        for hit in xss:
            data_num += len(json.loads(hit.data))
        data = {
            'owner_id': self.owner_id,
            'id': self.id,
            'name': self.name,
            'reflected': XSS.query.filter_by(client_id=self.id).filter_by(xss_type='reflected').count(),
            'stored': XSS.query.filter_by(client_id=self.id).filter_by(xss_type='stored').count(),
            'data': data_num
        }
        return data

    def to_dict_client(self):
        """Returns a dict containing client's data"""
        owner = None
        if self.owner_id != None:
            owner = User.query.filter_by(id=self.owner_id).first().username
        if owner == None:
            owner = 'Nobody'
        data = {
            'owner': owner,
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        return data

    def gen_uid(self):
        """Generates a UID"""
        characters = string.ascii_letters + string.digits
        new_uid = ''.join(random.choice(characters) for i in range(6))

        while(Client.query.filter_by(uid=new_uid).first() != None):
            new_uid = ''.join(random.choice(characters) for i in range(6))
        self.uid = new_uid


class XSS(db.Model):
    """Defines an XSS"""
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    headers = db.Column(db.Text)
    ip_addr = db.Column(db.String(15))
    data = db.Column(db.Text)
    timestamp = db.Column(db.Integer)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    xss_type = db.Column(db.String(9))

    def to_dict(self):
        """Returns full representation of XSS"""
        data = {
            'id': self.id,
            'headers': json.loads(self.headers),
            'ip_addr': self.ip_addr,
            'data': json.loads(self.data) if self.data != None else self.data,
            'timestamp': self.timestamp,
        }
        if 'fingerprint' in data['data'].keys():
            data['data']['fingerprint'] = ''
        if 'dom' in data['data'].keys():
            data['data']['dom'] = ''
        if 'screenshot' in data['data'].keys():
            data['data']['screenshot'] = ''

        return data

    def to_dict_short(self):
        """Returns an abridged representation of XSS"""
        data = {
            'id': self.id,
            'ip_addr': self.ip_addr,
            'timestamp': self.timestamp,
        }
        return data


class User(UserMixin, db.Model):
    """Defines a user"""
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(95), nullable=False)
    first_login = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    client = db.relationship('Client', backref='owner', lazy='dynamic')

    def set_password(self, password):
        """Sets user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Validates user's password"""
        return check_password_hash(self.password_hash, password)

    def generate_password(self):
        """Generates a new password"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(12))

    def to_dict(self):
        """Returns a representation of the user"""
        data = {
            'id': self.id,
            'username': self.username,
            'first_login': self.first_login,
            'is_admin': self.is_admin
        }
        return data


@login.user_loader
def load_user(id):
    """Returns the user identifier for the session mechanism"""
    return User.query.get(id)


def create_first_user(app):
    """Creates the admin user on application first launch"""
    with app.app_context():
        if db.session.query(User).count() != 0:
            print('[-] User creation not needed')
        else:
            user = User(username='admin', is_admin=1)
            user.set_password('xss')
            db.session.add(user)
            db.session.commit()
            print('[+] Initial user created')
