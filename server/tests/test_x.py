import json

from fixtures import client
from app.models import Client, XSS

from tests.test_login import login, logout


from tests.test_client import create_client, get_xss, get_xss_all


def test_normal_flow(client):

    login(client, 'admin', 'xss', True)

    create_client(client, 'TEST_NAME', 'Test description')

    client_obj = Client.query.filter_by(id=1).first()

    client.post('/api/x/r/{}'.format(client_obj.uid), data=dict(cookies='cookie=good', local_storage='{"local":"good"}',
                                                                session_storage='{"session":"good"}', param='good', fingerprint='["good"]', dom='<br />'))

    client.get('/api/x/s/{}'.format(client_obj.uid),
               headers={'X-Forwarded-For': '127.0.0.2'})

    xss1 = XSS.query.filter_by(id=1).first()
    xss2 = XSS.query.filter_by(id=2).first()

    xss1_json = json.loads(xss1.data)
    xss2_json = json.loads(xss2.data)

    assert xss1_json['cookies'][0] == {'cookie': 'good'}
    assert xss1_json['local_storage'][0] == {'local': 'good'}
    assert xss1_json['session_storage'][0] == {'session': 'good'}
    assert xss1_json['param'] == 'good'
    assert xss1_json['fingerprint'] == '[\"good\"]'
    assert xss1_json['dom'] == '<html>\n<br />\n</html>'
    assert xss1.xss_type == 'reflected'
    assert xss1.ip_addr == '127.0.0.1'
    for header in json.loads(xss1.headers):
        if 'User-Agent' in header.keys():
            assert 'werkzeug' in header['User-Agent']
    int(xss1.timestamp)

    assert xss2.xss_type == 'stored'
    assert xss2.ip_addr == '127.0.0.2'


def test_non_existent_client(client):

    rv = client.get('/api/x/r/AAAAA')

    assert rv._status_code == 200

    assert XSS.query.count() == 0
