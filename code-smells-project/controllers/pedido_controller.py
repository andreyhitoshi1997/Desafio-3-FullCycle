import logging

from flask import request, jsonify

from database import get_db
from models import pedido_model
from config.constants import (
    STATUSES_VALIDOS,
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


def criar():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens or len(itens) == 0:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    db = get_db()
    resultado = pedido_model.criar(db, usuario_id, itens)

    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

    logger.info(
        "Order %d created for user %d", resultado["pedido_id"], usuario_id
    )

    return jsonify(
        {
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }
    ), 201


def listar_por_usuario(usuario_id):
    db = get_db()
    page, per_page, offset = _parse_pagination()
    pedidos, total = pedido_model.get_por_usuario(
        db, usuario_id, limit=per_page, offset=offset
    )
    return jsonify(
        {
            "dados": pedidos,
            "sucesso": True,
            "paginacao": {"page": page, "per_page": per_page, "total": total},
        }
    ), 200


def listar_todos():
    db = get_db()
    page, per_page, offset = _parse_pagination()
    pedidos, total = pedido_model.get_todos(db, limit=per_page, offset=offset)
    return jsonify(
        {
            "dados": pedidos,
            "sucesso": True,
            "paginacao": {"page": page, "per_page": per_page, "total": total},
        }
    ), 200


def atualizar_status(pedido_id):
    dados = request.get_json()
    novo_status = dados.get("status", "")

    if novo_status not in STATUSES_VALIDOS:
        return jsonify({"erro": "Status inválido"}), 400

    db = get_db()
    pedido_model.atualizar_status(db, pedido_id, novo_status)

    if novo_status == "aprovado":
        logger.info("Order %d approved — preparing shipment", pedido_id)
    if novo_status == "cancelado":
        logger.info("Order %d cancelled — revert stock", pedido_id)

    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


def relatorio_vendas():
    db = get_db()
    relatorio = pedido_model.relatorio_vendas(db)
    return jsonify({"dados": relatorio, "sucesso": True}), 200
