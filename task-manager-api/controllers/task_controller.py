import logging
from datetime import datetime

from flask import request, jsonify
from sqlalchemy.orm import joinedload
from marshmallow import ValidationError

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from schemas.task_schema import TaskSchema, TaskUpdateSchema
from utils.helpers import VALID_STATUSES

logger = logging.getLogger(__name__)

_task_schema = TaskSchema()
_task_update_schema = TaskUpdateSchema()

DEFAULT_PER_PAGE = 1000  # effectively "all", preserves original unpaginated behavior
MAX_PER_PAGE = 100


def _parse_pagination():
    page = max(int(request.args.get("page", 1)), 1)
    if "per_page" in request.args:
        per_page = min(int(request.args["per_page"]), MAX_PER_PAGE)
    else:
        per_page = DEFAULT_PER_PAGE
    return page, per_page


def get_tasks():
    page, per_page = _parse_pagination()
    query = Task.query.options(joinedload(Task.user), joinedload(Task.category))
    tasks = query.offset((page - 1) * per_page).limit(per_page).all()
    return jsonify([t.to_dict() for t in tasks]), 200


def get_task(task_id):
    task = Task.query.options(
        joinedload(Task.user), joinedload(Task.category)
    ).get(task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    return jsonify(task.to_dict()), 200


def _parse_due_date(value):
    return datetime.strptime(value, "%Y-%m-%d")


def create_task():
    data = request.get_json() or {}
    payload = _task_schema.load(data)  # raises ValidationError -> centralized handler

    user_id = payload.get("user_id")
    if user_id:
        if not User.query.get(user_id):
            return jsonify({"error": "Usuário não encontrado"}), 404

    category_id = payload.get("category_id")
    if category_id:
        if not Category.query.get(category_id):
            return jsonify({"error": "Categoria não encontrada"}), 404

    task = Task()
    task.title = payload["title"]
    task.description = payload.get("description", "")
    task.status = payload.get("status", "pending")
    task.priority = payload.get("priority", 3)
    task.user_id = user_id
    task.category_id = category_id

    if payload.get("due_date"):
        try:
            task.due_date = _parse_due_date(payload["due_date"])
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD"}), 400

    tags = payload.get("tags")
    if tags:
        task.tags = ",".join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    logger.info("Task criada: %s - %s", task.id, task.title)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    data = request.get_json() or {}
    payload = _task_update_schema.load(data)

    if "title" in payload:
        task.title = payload["title"]
    if "description" in payload:
        task.description = payload["description"]
    if "status" in payload:
        task.status = payload["status"]
    if "priority" in payload:
        task.priority = payload["priority"]

    if "user_id" in payload:
        if payload["user_id"] and not User.query.get(payload["user_id"]):
            return jsonify({"error": "Usuário não encontrado"}), 404
        task.user_id = payload["user_id"]

    if "category_id" in payload:
        if payload["category_id"] and not Category.query.get(payload["category_id"]):
            return jsonify({"error": "Categoria não encontrada"}), 404
        task.category_id = payload["category_id"]

    if "due_date" in payload:
        if payload["due_date"]:
            try:
                task.due_date = _parse_due_date(payload["due_date"])
            except ValueError:
                return jsonify({"error": "Formato de data inválido"}), 400
        else:
            task.due_date = None

    if "tags" in payload:
        tags = payload["tags"]
        task.tags = ",".join(tags) if isinstance(tags, list) else tags

    db.session.commit()
    logger.info("Task atualizada: %s", task.id)
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    db.session.delete(task)
    db.session.commit()
    logger.info("Task deletada: %s", task_id)
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    query_text = request.args.get("q", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    user_id = request.args.get("user_id", "")

    query = Task.query.options(joinedload(Task.user), joinedload(Task.category))

    if query_text:
        query = query.filter(
            db.or_(
                Task.title.like(f"%{query_text}%"),
                Task.description.like(f"%{query_text}%"),
            )
        )
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == int(priority))
    if user_id:
        query = query.filter(Task.user_id == int(user_id))

    return jsonify([t.to_dict() for t in query.all()]), 200


def task_stats():
    total = Task.query.count()
    counts = {status: Task.query.filter_by(status=status).count() for status in VALID_STATUSES}
    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())

    stats = {
        "total": total,
        "pending": counts["pending"],
        "in_progress": counts["in_progress"],
        "done": counts["done"],
        "cancelled": counts["cancelled"],
        "overdue": overdue_count,
        "completion_rate": round((counts["done"] / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200
