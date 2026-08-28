import logging

from flask import request, jsonify
from marshmallow import ValidationError

from database import db
from models.user import User
from models.task import Task
from schemas.user_schema import UserSchema, UserUpdateSchema, LoginSchema
from middlewares.auth import generate_token

logger = logging.getLogger(__name__)

_user_schema = UserSchema()
_user_update_schema = UserUpdateSchema()
_login_schema = LoginSchema()


def get_users():
    users = User.query.all()
    result = []
    for u in users:
        data = u.to_dict()
        data["task_count"] = len(u.tasks)
        result.append(data)
    return jsonify(result), 200


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = user.to_dict()
    data["tasks"] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return jsonify(data), 200


def create_user():
    data = request.get_json() or {}
    payload = _user_schema.load(data)

    if User.query.filter_by(email=payload["email"]).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    user = User()
    user.name = payload["name"]
    user.email = payload["email"]
    user.set_password(payload["password"])
    user.role = payload.get("role", "user")

    db.session.add(user)
    db.session.commit()
    logger.info("Usuário criado: %s - %s", user.id, user.name)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json() or {}
    payload = _user_update_schema.load(data)

    if "name" in payload:
        user.name = payload["name"]

    if "email" in payload:
        existing = User.query.filter_by(email=payload["email"]).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "Email já cadastrado"}), 409
        user.email = payload["email"]

    if "password" in payload:
        user.set_password(payload["password"])

    if "role" in payload:
        user.role = payload["role"]

    if "active" in payload:
        user.active = payload["active"]

    db.session.commit()
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    for t in tasks:
        db.session.delete(t)

    db.session.delete(user)
    db.session.commit()
    logger.info("Usuário deletado: %s", user_id)
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


def login():
    data = request.get_json() or {}
    payload = _login_schema.load(data)

    user = User.query.filter_by(email=payload["email"]).first()
    if not user or not user.check_password(payload["password"]):
        return jsonify({"error": "Credenciais inválidas"}), 401

    if not user.active:
        return jsonify({"error": "Usuário inativo"}), 403

    token = generate_token(user)
    return jsonify(
        {
            "message": "Login realizado com sucesso",
            "user": user.to_dict(),
            "token": token,
        }
    ), 200
