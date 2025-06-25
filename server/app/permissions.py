import uuid
from enum import StrEnum
from functools import wraps
from typing import Any, Callable, Optional, cast

import flask_jwt_extended
import jwt
from app import db
from app.schemas import XSS, ApiKey, Client, User
from flask import current_app, g, request
from werkzeug.exceptions import HTTPException


class Permission(StrEnum):
    ADMIN = "admin"
    OWNER = "owner"


class InvalidApiKeyException(HTTPException):
    pass


def authorization_required(optional: bool = False, refresh: bool = False) -> Callable:
    def wrapper(decorated_function) -> Callable:
        @wraps(decorated_function)
        def decorator(*args, **kwargs) -> Any:
            # Check if an api key header is present
            # If refresh is required, then skip the API key check as we want an actual jwt
            if (api_key := _get_api_key_header()) is not None and refresh is False:
                try:
                    _validate_api_key(api_key)
                except InvalidApiKeyException:
                    # If optional was True, then do not return an error
                    if optional is False:
                        return {"msg": "Invalid API key"}, 401
            else:
                # If no api key was found, check the jwt
                try:
                    flask_jwt_extended.verify_jwt_in_request(optional=optional, refresh=refresh)
                except jwt.exceptions.DecodeError:
                    return {"msg": "Invalid token"}, 422

            return current_app.ensure_sync(decorated_function)(*args, **kwargs)

        return decorator

    return wrapper


def _get_api_key_header() -> Optional[str]:
    authorization_header = request.headers.get("Authorization")
    if authorization_header:
        key = authorization_header.removeprefix("Bearer ")
        if _is_valid_uuid4(key):
            return key


def _is_valid_uuid4(value: str) -> bool:
    try:
        uuid4 = uuid.UUID(value, version=4)
    except ValueError:
        return False
    return str(uuid4) == value


def _validate_api_key(key: str) -> None:
    api_key = db.session.execute(db.select(ApiKey).filter_by(key=key)).scalar_one_or_none()
    if api_key is not None:
        g._api_key_user = {"loaded_user": api_key.owner}
    else:
        raise InvalidApiKeyException


def get_current_user() -> User:
    if "_api_key_user" in g:
        return g._api_key_user["loaded_user"]
    else:
        return flask_jwt_extended.get_current_user()


def permissions(all_of: Optional[set[Permission]] = None, any_of: Optional[set[Permission]] = None) -> Callable:
    def wrapper(decorated_function: Callable) -> Callable:
        @wraps(decorated_function)
        def decorator(*args, **kwargs) -> Any:
            current_user: User = get_current_user()

            permission_attributes = {"admin": current_user.is_admin, "owner": False}

            if "user_id" in kwargs:
                permission_attributes["owner"] = current_user.id == kwargs["user_id"]
            elif "client_id" in kwargs:
                client: Client = db.first_or_404(db.select(Client).filter_by(id=kwargs["client_id"]))
                permission_attributes["owner"] = current_user.id == client.owner_id
            elif "key_id" in kwargs:
                api_key: ApiKey = db.first_or_404(db.select(ApiKey).filter_by(id=kwargs["key_id"]))
                permission_attributes["owner"] = current_user.id == api_key.owner_id
            elif "xss_id" in kwargs:
                xss: XSS = db.first_or_404(db.select(XSS).filter_by(id=kwargs["xss_id"]))
                client: Client = cast(Client, xss.client)  # type: ignore
                permission_attributes["owner"] = current_user.id == client.owner_id

            if all_of:
                values_to_check = [v for k, v in permission_attributes.items() if k in all_of]
                if all(values_to_check):
                    return current_app.ensure_sync(decorated_function)(*args, **kwargs)
            elif any_of:
                values_to_check = [v for k, v in permission_attributes.items() if k in any_of]
                if any(values_to_check):
                    return current_app.ensure_sync(decorated_function)(*args, **kwargs)

            return {"msg": "Forbidden"}, 403

        return decorator

    return wrapper
