import json

from fixtures import client
from tests.test_login import login, logout
from app.models import Client


def create_client(client, name, description):
    return client.put('/api/client', data=dict(name=name, description=description))


def get_client(client, id):
    return client.get('/api/client/{}'.format(id))


def edit_client(client, id, **kwargs):
    return client.post('/api/client/{}'.format(id), data=kwargs)


def get_xss_all(client, id, flavor):
    return client.get('/api/client/{}/{}/all'.format(id, flavor))


def get_xss(client, client_id, xss_id):
    return client.get('/api/client/{}/{}'.format(client_id, xss_id))


def test_new_client(client):

    login(client, 'admin', 'xss', False)

    rv = client.put('/api/client', data=dict(name='test1'))
    assert b'Missing name or description' in rv.data

    rv = client.put('/api/client', data=dict(description='desc1'))
    assert b'Missing name or description' in rv.data

    client.put(
        '/api/client', data=dict(name='name1', description='desc1'))

    client1 = Client.query.filter_by(id=1).first()

    assert client1.name == 'name1'

    rv = client.put(
        '/api/client', data=dict(name='name1', description='desc1'))

    assert b'Client already exists' in rv.data

    rv = client.put('/api/client', data=dict(name='', description='desc1'))
    assert b'Invalid data (name empty or too long or description too long)' in rv.data
    rv = client.put('/api/client', data=dict(name='a'*33, description='desc1'))
    assert b'Invalid data (name empty or too long or description too long)' in rv.data
    rv = client.put(
        '/api/client', data=dict(name='test2', description='a'*129))
    assert b'Invalid data (name empty or too long or description too long)' in rv.data


def test_get_client(client):
    login(client, 'admin', 'xss', False)
    client.put(
        '/api/client', data=dict(name='name1', description='desc1'))

    rv = get_client(client, 1)
    assert json.loads(rv.data)['name'] == 'name1'


def test_edit_client(client):
    login(client, 'admin', 'xss', False)
    client.put(
        '/api/client', data=dict(name='name1', description='desc1'))

    
