from functools import wraps
from datetime import timedelta

import jwt
from flask import request, jsonify

from config.settings import Settings
from utils.helpers import utcnow


def generate_token(user):
    payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": utcnow() + timedelta(hours=Settings.JWT_EXP_HOURS),
        "iat": utcnow(),
    }
    return jwt.encode(payload, Settings.SECRET_KEY, algorithm="HS256")


def require_auth(f):
    """Requires a valid `Authorization: Bearer <token>` header.

    Applied to mutating endpoints (create/update/delete). Read-only (GET)
    endpoints and POST /users (registration) / POST /login stay public —
    see README for the full policy.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token de autenticação ausente"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        request.user_id = payload["user_id"]
        request.user_role = payload["role"]
        return f(*args, **kwargs)

    return decorated
