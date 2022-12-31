import uuid
from functools import wraps
from typing import Callable, List, Optional

import flask_jwt_extended
from app import db
from app.models import XSS, ApiKey, Client, User
from flask import current_app, g, request


class UserLookupError(Exception):
    pass


def authorization_required(optional: bool = False, refresh: bool = False):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if not _verify_api_key_in_request():
                flask_jwt_extended.verify_jwt_in_request(optional=optional, refresh=refresh)
            return current_app.ensure_sync(fn)(*args, **kwargs)

        return decorator

    return wrapper


def _verify_api_key_in_request() -> bool:
    api_key = _get_api_key_from_request()

    if api_key:
        g._apikey_user = {"loaded_user": _get_user_from_api_key(api_key=api_key)}
        return True

    return False


def _get_api_key_from_request() -> Optional[ApiKey]:
    authorization_header = request.headers.get("Authorization")
    if authorization_header:
        key = authorization_header.removeprefix("Bearer ")
        if _is_valid_uuid4(key):
            return db.session.query(ApiKey).filter_by(key=key).first()


def _get_user_from_api_key(api_key: ApiKey) -> User:
    user: User = db.session.query(User).filter_by(id=api_key.owner_id).first()
    if user:
        return user
    else:
        raise UserLookupError


def _is_valid_uuid4(value: str) -> bool:
    try:
        uuid4 = uuid.UUID(value, version=4)
    except ValueError:
        return False
    return str(uuid4) == value


def get_current_user() -> User:
    api_key_user_dict = g.get("_apikey_user")
    if api_key_user_dict:
        return api_key_user_dict["loaded_user"]
    else:
        return flask_jwt_extended.get_current_user()


def permissions(all_of: List[str] = [], one_of: List[str] = []):
    def wrapper(fn: Callable):
        @wraps(fn)
        def decorator(*args, **kwargs):
            current_user: User = get_current_user()

            permission_attributes = {"admin": current_user.is_admin}

            if "user_id" in kwargs:
                permission_attributes["owner"] = current_user.id == kwargs["user_id"]
            elif "client_id" in kwargs:
                client: Client = db.session.query(Client).filter_by(id=kwargs["client_id"]).first_or_404()
                permission_attributes["owner"] = current_user.id == client.owner_id
            elif "xss_id" in kwargs:
                xss: XSS = db.session.query(XSS).filter_by(id=kwargs["xss_id"]).first_or_404()
                permission_attributes["owner"] = current_user.id == xss.client.owner_id
            elif "key_id" in kwargs:
                api_key: ApiKey = db.session.query(ApiKey).filter_by(id=kwargs["key_id"]).first_or_404()
                permission_attributes["owner"] = current_user.id == api_key.owner_id

            if all_of:
                values_to_check = [v for k, v in permission_attributes.items() if k in all_of]
                if all(values_to_check):
                    return fn(*args, **kwargs)
            elif one_of:
                values_to_check = [v for k, v in permission_attributes.items() if k in one_of]
                if any(values_to_check):
                    return fn(*args, **kwargs)

            return {"msg": "Forbidden"}, 403

        return decorator

    return wrapper
