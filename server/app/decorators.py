from functools import wraps

from app.models import XSS, Client
from flask import jsonify
from flask_jwt_extended import get_current_user


def permissions(all_of=[], one_of=[]):
    """Manages permissions"""

    current_user = get_current_user()

    def deco(orig_func):
        @wraps(orig_func)
        def new_func(*args, **kwargs):
            if len(all_of) != 0:
                if "admin" in all_of:
                    if not current_user.is_admin:
                        return jsonify({"status": "error", "detail": "Only an administrator can do that"}), 403

                if "owner" in all_of:
                    if "client_id" in kwargs:
                        client = Client.query.filter_by(id=kwargs["client_id"]).first_or_404()
                        if current_user.id != client.owner_id:
                            return jsonify({"status": "error", "detail": "You are not the client's owner"}), 403

                    if "xss_id" in kwargs:
                        xss = XSS.query.filter_by(id=kwargs["xss_id"]).first_or_404()
                        if current_user.id != xss.client.owner_id:
                            return jsonify({"status": "error", "detail": "You are not the client's owner"}), 403

                return orig_func(*args, **kwargs)

            elif len(one_of) != 0:
                if "admin" in one_of:
                    if current_user.is_admin:
                        return orig_func(*args, **kwargs)

                if "owner" in one_of:
                    if "client_id" in kwargs:
                        client = Client.query.filter_by(id=kwargs["client_id"]).first_or_404()
                        if current_user.id == client.owner_id:
                            return orig_func(*args, **kwargs)
                    if "xss_id" in kwargs:
                        xss = XSS.query.filter_by(id=kwargs["xss_id"]).first_or_404()
                        if current_user.id == xss.client.owner_id:
                            return orig_func(*args, **kwargs)

                return jsonify({"status": "error", "detail": "Insufficient permissions"}), 403

            else:
                return orig_func(*args, **kwargs)

        return new_func

    return deco
