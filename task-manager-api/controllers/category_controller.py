from flask import request, jsonify

from database import db
from models.category import Category
from models.task import Task


def get_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        data = c.to_dict()
        data["task_count"] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return jsonify(result), 200


def create_category():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    name = data.get("name")
    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400

    category = Category()
    category.name = name
    category.description = data.get("description", "")
    category.color = data.get("color", "#000000")

    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return jsonify({"error": "Categoria não encontrada"}), 404

    data = request.get_json() or {}
    if "name" in data:
        cat.name = data["name"]
    if "description" in data:
        cat.description = data["description"]
    if "color" in data:
        cat.color = data["color"]

    db.session.commit()
    return jsonify(cat.to_dict()), 200


def delete_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return jsonify({"error": "Categoria não encontrada"}), 404

    db.session.delete(cat)
    db.session.commit()
    return jsonify({"message": "Categoria deletada"}), 200
