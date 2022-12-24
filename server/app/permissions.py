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

            permission_attributes = {"admin": current_user.is_admin}

            if "user_id" in kwargs:
                permission_attributes["owner"] = current_user.id == kwargs["user_id"]
            elif "client_id" in kwargs:
                client: Client = db.session.query(Client).filter_by(id=kwargs["client_id"]).first_or_404()
                permission_attributes["owner"] = current_user.id == client.owner_id
            elif "xss_id" in kwargs:
                xss: XSS = db.session.query(XSS).filter_by(id=kwargs["xss_id"]).first_or_404()
                permission_attributes["owner"] = current_user.id == xss.client.owner_id

            if all_of:
                values_to_check = [v for k, v in permission_attributes.items() if k in all_of]
                if all(values_to_check):
                    return original_function(*args, **kwargs)
            elif one_of:
                values_to_check = [v for k, v in permission_attributes.items() if k in one_of]
                if any(values_to_check):
                    return original_function(*args, **kwargs)

            return {"msg": "Forbidden"}, 403

        return new_function

    return decorator
