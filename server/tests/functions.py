# client
import json


def create_client(client, headers, **kwargs):
    return client.post("/api/client", data=json.dumps(kwargs), content_type="application/json", headers=headers)


def get_client(client, headers, id):
    return client.get(f"/api/client/{id}", headers=headers)


def edit_client(client, headers, id, **kwargs):
    return client.patch(f"/api/client/{id}", data=json.dumps(kwargs), content_type="application/json", headers=headers)


def delete_client(client, headers, client_id):
    return client.delete(f"/api/client/{client_id}", headers=headers)


def get_clients(client, headers):
    return client.get("/api/client", headers=headers)


# login


def login(client, headers, **kwargs):
    return client.post("/api/auth/login", data=json.dumps(kwargs), content_type="application/json", headers=headers)


def logout(client, headers):
    return client.post("/api/auth/logout", headers=headers)


def refresh(client, headers):
    return client.post("/api/auth/refresh", headers=headers)


def login_get_headers(client, username, password):
    tokens = json.loads(login(client, {}, username=username, password=password).data)["detail"]
    access_header = {"Authorization": f"Bearer {tokens['access_token']}"}
    refresh_header = {"Authorization": f"Bearer {tokens['refresh_token']}"}
    return access_header, refresh_header


# x


def post_x(client, headers, xss_type, uid, **kwargs):
    return client.post(f"/api/x/{xss_type}/{uid}", data=json.dumps(kwargs), content_type="application/json", headers=headers)


def get_x(client, headers, xss_type, uid, **kwargs):
    return client.get(f"/api/x/{xss_type}/{uid}", query_string=kwargs, headers=headers)


# settings


def patch_settings(client, headers, **kwargs):
    return client.patch("/api/settings", data=json.dumps(kwargs), content_type="application/json", headers=headers)


def get_settings(client, headers):
    return client.get("/api/settings", headers=headers)


def send_test_mail(client, headers, **kwargs):
    return client.post("/api/settings/smtp_test", data=json.dumps(kwargs), content_type="application/json", headers=headers)


# users


def new_user(client, headers, **kwargs):
    return client.post("/api/user", data=json.dumps(kwargs), content_type="application/json", headers=headers)


def change_password(client, headers, **kwargs):
    return client.post("/api/user/password", data=json.dumps(kwargs), content_type="application/json", headers=headers)


def reset_password(client, headers, id, **kwargs):
    return client.post(f"/api/user/{id}/password", data=json.dumps(kwargs), content_type="application/json", headers=headers)


def get_user(client, headers):
    return client.get("/api/user/current", headers=headers)


def delete_user(client, headers, id):
    return client.delete(f"/api/user/{id}", headers=headers)


def edit_user(client, headers, id, **kwargs):
    return client.patch(f"/api/user/{id}", data=json.dumps(kwargs), content_type="application/json", headers=headers)


def get_users(client, headers):
    return client.get("/api/user", headers=headers)


# xss


def generate_payload(client, headers, **kwargs):
    return client.get(f"/api/xss/generate", query_string=kwargs, headers=headers)


def delete_xss(client, headers, id):
    return client.delete(f"/api/xss/{id}", headers=headers)


def get_loot_type(client, headers, id, loot_type):
    return client.get(f"/api/xss/{id}/data/{loot_type}", headers=headers)


def delete_loot_type(client, headers, id, loot_type):
    return client.delete(f"/api/xss/{id}/data/{loot_type}", headers=headers)


def get_xss_all(client, headers, **kwargs):
    return client.get(f"/api/xss", query_string=kwargs, headers=headers)


def get_xss(client, headers, xss_id):
    return client.get(f"/api/xss/{xss_id}", headers=headers)


def get_loot(client, headers, **kwargs):
    return client.get("/api/xss/data", query_string=kwargs, headers=headers)
