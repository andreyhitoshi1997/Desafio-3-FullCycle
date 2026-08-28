import logging

from flask import request, jsonify

from database import get_db
from models import usuario_model
from config.constants import (
    PAGINACAO_DEFAULT_PAGE,
    PAGINACAO_DEFAULT_PER_PAGE,
    PAGINACAO_MAX_PER_PAGE,
)

logger = logging.getLogger(__name__)


def _parse_pagination():
    page = max(int(request.args.get("page", PAGINACAO_DEFAULT_PAGE)), 1)
    per_page = min(
        int(request.args.get("per_page", PAGINACAO_DEFAULT_PER_PAGE)),
        PAGINACAO_MAX_PER_PAGE,
    )
    offset = (page - 1) * per_page
    return page, per_page, offset


def listar():
    db = get_db()
    page, per_page, offset = _parse_pagination()
    usuarios, total = usuario_model.get_todos(db, limit=per_page, offset=offset)
    return jsonify(
        {
            "dados": usuarios,
            "sucesso": True,
            "paginacao": {"page": page, "per_page": per_page, "total": total},
        }
    ), 200


def buscar_por_id(usuario_id):
    db = get_db()
    usuario = usuario_model.get_por_id(db, usuario_id)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True}), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404


def criar():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    db = get_db()
    novo_id = usuario_model.criar(db, nome, email, senha)
    logger.info("User created: %s", email)
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


def login():
    dados = request.get_json()
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    db = get_db()
    usuario = usuario_model.autenticar(db, email, senha)
    if usuario:
        logger.info("Login successful: %s", email)
        return jsonify(
            {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}
        ), 200

    logger.info("Login failed: %s", email)
    return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
