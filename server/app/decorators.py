from functools import wraps
from typing import Callable, List

from app import db
from app.models import XSS, Client, User
from flask_jwt_extended import get_current_user


def permissions(all_of: List[str] = [], one_of: List[str] = []):
    def decorator(original_function: Callable):
        @wraps(original_function)
        def new_function(*args, **kwargs):
            current_user: User = get_current_user()

            permission_attributes = [current_user.is_admin]

            if "client_id" in kwargs:
                client: Client = db.session.query(Client).filter_by(id=kwargs["client_id"]).first_or_404()
                permission_attributes.append(current_user.id == client.owner_id)
            elif "xss_id" in kwargs:
                xss: XSS = db.session.query(XSS).filter_by(id=kwargs["xss_id"]).first_or_404()
                permission_attributes.append(current_user.id == xss.client.owner_id)

            if (all_of and all(permission_attributes)) or (one_of and any(permission_attributes)) or (not all_of and not one_of):
                return original_function(*args, **kwargs)

            return {"msg": "Forbidden"}, 403

        return new_function

    return decorator
