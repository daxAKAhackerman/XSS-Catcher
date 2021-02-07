# client
import json


def create_client(client, **kwargs):
    return client.post("/api/client", data=json.dumps(kwargs), content_type="application/json")


def get_client(client, id):
    return client.get(f"/api/client/{id}")


def edit_client(client, id, **kwargs):
    return client.patch(f"/api/client/{id}", data=json.dumps(kwargs), content_type="application/json")


def delete_client(client, client_id):
    return client.delete(f"/api/client/{client_id}")


def get_clients(client):
    return client.get("/api/client")


# login


def login(client, **kwargs):
    return client.post("/api/auth/login", data=json.dumps(kwargs), content_type="application/json")


def logout(client):
    return client.get("/api/auth/logout")


# x


def post_x(client, xss_type, uid, **kwargs):
    return client.post(f"/api/x/{xss_type}/{uid}", data=json.dumps(kwargs), content_type="application/json")


def get_x(client, xss_type, uid, headers={}, **kwargs):
    return client.get(f"/api/x/{xss_type}/{uid}", query_string=kwargs, headers=headers)


# settings


def patch_settings(client, **kwargs):
    return client.patch("/api/settings", data=json.dumps(kwargs), content_type="application/json")


def get_settings(client):
    return client.get("/api/settings")


def send_test_mail(client, **kwargs):
    return client.post("/api/settings/smtp_test", data=json.dumps(kwargs), content_type="application/json")


# users


def new_user(client, **kwargs):
    return client.post("/api/user", data=json.dumps(kwargs), content_type="application/json")


def change_password(client, **kwargs):
    return client.post("/api/user/password", data=json.dumps(kwargs), content_type="application/json")


def reset_password(client, id, **kwargs):
    return client.post(f"/api/user/{id}/password", data=json.dumps(kwargs), content_type="application/json")


def get_user(client):
    return client.get("/api/user/current")


def delete_user(client, id):
    return client.delete(f"/api/user/{id}")


def edit_user(client, id, **kwargs):
    return client.patch(f"/api/user/{id}", data=json.dumps(kwargs), content_type="application/json")


def get_users(client):
    return client.get("/api/user")


# xss


def generate_payload(client, **kwargs):
    return client.get(f"/api/xss/generate", query_string=kwargs)


def delete_xss(client, id):
    return client.delete(f"/api/xss/{id}")


def get_loot_type(client, id, loot_type):
    return client.get(f"/api/xss/{id}/data/{loot_type}")


def delete_loot_type(client, id, loot_type):
    return client.delete(f"/api/xss/{id}/data/{loot_type}")


def get_xss_all(client, **kwargs):
    return client.get(f"/api/xss", query_string=kwargs)


def get_xss(client, xss_id):
    return client.get(f"/api/xss/{xss_id}")


def get_loot(client, **kwargs):
    return client.get("/api/xss/data", query_string=kwargs)
