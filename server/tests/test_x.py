import json

from fixtures import client
from app.models import Client

from tests.test_login import login, logout


def create_client(client, name, description):
    return client.put('/api/client', data=dict(name=name, description=description))


def get_xss_all(client, id, flavor):
    return client.get('/api/client/{}/{}/all'.format(id, flavor))


def get_xss(client, client_id, xss_id):
    return client.get('/api/client/{}/{}'.format(client_id, xss_id))


def test_normal_flow(client):

    login(client, 'admin', 'xss', True)

    create_client(client, 'TEST_NAME', 'Test description')

    client_obj = Client.query.filter_by(id=1).first()

    client.post('/api/x/r/{}'.format(client_obj.uid), data=dict(cookies='cookie=good', local_storage='{"local":"good"}',
                                                                session_storage='{"session":"good"}', origin_url='good', param='good', fingerprint='["good"]', dom='<br />'))

    client.get('/api/x/s/{}'.format(client_obj.uid),
               headers={'X-Forwarded-For': '127.0.0.1'})

    rv = get_xss(client, 1, 1)


def test_non_existent_client(client):

    rv = client.get('/api/x/r/AAAAA')

    assert rv._status_code == 200
