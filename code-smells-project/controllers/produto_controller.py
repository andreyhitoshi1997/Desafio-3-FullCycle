import logging

from flask import request, jsonify

from database import get_db
from models import produto_model
from config.constants import (
    CATEGORIAS_VALIDAS,
    NOME_MIN_LENGTH,
    NOME_MAX_LENGTH,
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
    produtos, total = produto_model.get_todos(db, limit=per_page, offset=offset)
    logger.info("Listed %d products (page %d)", len(produtos), page)
    return jsonify(
        {
            "dados": produtos,
            "sucesso": True,
            "paginacao": {"page": page, "per_page": per_page, "total": total},
        }
    ), 200


def buscar_por_id(produto_id):
    db = get_db()
    produto = produto_model.get_por_id(db, produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    if "nome" not in dados:
        return jsonify({"erro": "Nome é obrigatório"}), 400
    if "preco" not in dados:
        return jsonify({"erro": "Preço é obrigatório"}), 400
    if "estoque" not in dados:
        return jsonify({"erro": "Estoque é obrigatório"}), 400

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        return jsonify({"erro": "Preço não pode ser negativo"}), 400
    if estoque < 0:
        return jsonify({"erro": "Estoque não pode ser negativo"}), 400
    if len(nome) < NOME_MIN_LENGTH:
        return jsonify({"erro": "Nome muito curto"}), 400
    if len(nome) > NOME_MAX_LENGTH:
        return jsonify({"erro": "Nome muito longo"}), 400
    if categoria not in CATEGORIAS_VALIDAS:
        return jsonify(
            {"erro": "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)}
        ), 400

    db = get_db()
    novo_id = produto_model.criar(db, nome, descricao, preco, estoque, categoria)
    logger.info("Product created with ID: %d", novo_id)
    return jsonify(
        {"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}
    ), 201


def atualizar(produto_id):
    dados = request.get_json()
    db = get_db()

    produto_existente = produto_model.get_por_id(db, produto_id)
    if not produto_existente:
        return jsonify({"erro": "Produto não encontrado"}), 404

    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    if "nome" not in dados:
        return jsonify({"erro": "Nome é obrigatório"}), 400
    if "preco" not in dados:
        return jsonify({"erro": "Preço é obrigatório"}), 400
    if "estoque" not in dados:
        return jsonify({"erro": "Estoque é obrigatório"}), 400

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        return jsonify({"erro": "Preço não pode ser negativo"}), 400
    if estoque < 0:
        return jsonify({"erro": "Estoque não pode ser negativo"}), 400

    produto_model.atualizar(db, produto_id, nome, descricao, preco, estoque, categoria)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar(produto_id):
    db = get_db()
    produto = produto_model.get_por_id(db, produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto_model.deletar(db, produto_id)
    logger.info("Product %d deleted", produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)

    db = get_db()
    resultados = produto_model.buscar(db, termo, categoria, preco_min, preco_max)
    return jsonify(
        {"dados": resultados, "total": len(resultados), "sucesso": True}
    ), 200
