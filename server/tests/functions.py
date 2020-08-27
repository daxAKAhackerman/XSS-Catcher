# client


def create_client(client, **kwargs):
    return client.put('/api/client', data=kwargs)


def get_client(client, id):
    return client.get('/api/client/{}'.format(id))


def edit_client(client, id, **kwargs):
    return client.post('/api/client/{}'.format(id), data=kwargs)


def get_xss_all(client, id, flavor):
    return client.get('/api/client/{}/{}/all'.format(id, flavor))


def get_xss(client, client_id, xss_id):
    return client.get('/api/client/{}/{}'.format(client_id, xss_id))


def delete_client(client, client_id):
    return client.delete('/api/client/{}'.format(client_id))


def get_single_xss(client, client_id, xss_id):
    return client.get('/api/client/{}/{}'.format(client_id, xss_id))


def get_loot(client, client_id):
    return client.get('/api/client/{}/loot'.format(client_id))


def get_clients(client):
    return client.get('/api/client/all')


# login


def login(client, **kwargs):
    return client.post('/api/auth/login', data=kwargs)


def logout(client):
    return client.get('/api/auth/logout')


# x

def post_x(client, xss_type, uid, **kwargs):
    return client.post('/api/x/{}/{}'.format(xss_type, uid), data=kwargs)


def get_x(client, xss_type, uid, headers={}, **kwargs):
    query_string = '?'
    for i in kwargs:
        query_string += '{}={}&'.format(i, kwargs[i])
    query_string = query_string.rstrip('&')
    return client.get('/api/x/{}/{}{}'.format(xss_type, uid, query_string), headers=headers)


# settings

def post_settings(client, **kwargs):
    return client.post('/api/settings', data=kwargs)


def get_settings(client):
    return client.get('/api/settings')


def send_test_mail(client, **kwargs):
    return client.post('/api/settings/smtp_test', data=kwargs)


# users

def new_user(client, **kwargs):
    return client.post('/api/user/new', data=kwargs)


def change_password(client, **kwargs):
    return client.post('/api/user/change_password', data=kwargs)


def reset_password(client, id, **kwargs):
    return client.post('/api/user/{}/reset_password'.format(id), data=kwargs)


def get_user(client):
    return client.get('/api/user')


def delete_user(client, id):
    return client.delete('/api/user/{}'.format(id))


def edit_user(client, id, **kwargs):
    return client.post('/api/user/{}'.format(id), data=kwargs)


def get_users(client):
    return client.get('/api/user/all')


# xss

def generate_payload(client, id, **kwargs):
    query_string = '?'
    for i in kwargs:
        query_string += '{}={}&'.format(i, kwargs[i])
    query_string = query_string.rstrip('&')
    return client.get('/api/xss/generate/{}{}'.format(id, query_string))


def delete_xss(client, id):
    return client.delete('/api/xss/{}'.format(id))


def get_loot_type(client, id, loot_type):
    return client.get('/api/xss/{}/{}'.format(id, loot_type))


def delete_loot_type(client, id, loot_type):
    return client.delete('/api/xss/{}/{}'.format(id, loot_type))
