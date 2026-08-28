from functools import wraps

from flask import request, jsonify

from config.settings import Settings


def require_admin_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Admin-Token", "")
        if token != Settings.ADMIN_TOKEN:
            return jsonify({"erro": "Token de admin inválido"}), 403
        return f(*args, **kwargs)

    return decorated
