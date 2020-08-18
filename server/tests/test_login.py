from fixtures import client


def login(client, username, password, remember):
    return client.post('/api/auth/login', data=dict(username=username, password=password, remember=remember), follow_redirects=True)


def logout(client):
    return client.get('/api/auth/logout', follow_redirects=True)


def test_normal_flow(client):

    rv = login(client, 'admin', 'xss', True)
    assert b'OK' in rv.data

    rv = logout(client)
    assert b'OK' in rv.data


def test_login_required(client):
    rv = logout(client)
    assert rv._status_code == 401


def test_bad_flow(client):
    login(client, 'admin', 'xss', True)

    rv = login(client, 'admin', 'xss', True)
    assert b'Already logged in' in rv.data


def test_missing_data(client):
    rv = client.post('/api/auth/login', data=dict(username='admin',
                                                  remember=True), follow_redirects=True)
    assert b'Missing username or password' in rv.data

    rv = client.post('/api/auth/login', data=dict(password='xss',
                                                  remember=True), follow_redirects=True)
    assert b'Missing username or password' in rv.data

    rv = client.post('/api/auth/login', data=dict(username='admin',
                                                  password='xss'), follow_redirects=True)
    assert b'OK' in rv.data


def test_bad_creds(client):
    rv = login(client, 'bad_username', 'bad_password', True)
    assert b'Bad username or password' in rv.data

    rv = login(client, 'admin', 'bad_password', True)
    assert b'Bad username or password' in rv.data
