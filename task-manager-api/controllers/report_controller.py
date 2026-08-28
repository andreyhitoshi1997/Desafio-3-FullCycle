from collections import defaultdict

from flask import jsonify

from models.task import Task
from models.user import User
from models.category import Category
from utils.helpers import utcnow
from datetime import timedelta


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status="pending").count()
    in_progress = Task.query.filter_by(status="in_progress").count()
    done = Task.query.filter_by(status="done").count()
    cancelled = Task.query.filter_by(status="cancelled").count()

    p1 = Task.query.filter_by(priority=1).count()
    p2 = Task.query.filter_by(priority=2).count()
    p3 = Task.query.filter_by(priority=3).count()
    p4 = Task.query.filter_by(priority=4).count()
    p5 = Task.query.filter_by(priority=5).count()

    all_tasks = Task.query.all()
    overdue_count = 0
    overdue_list = []
    tasks_by_user = defaultdict(list)
    for t in all_tasks:
        if t.is_overdue():
            overdue_count += 1
            overdue_list.append(
                {
                    "id": t.id,
                    "title": t.title,
                    "due_date": str(t.due_date),
                    "days_overdue": (utcnow() - t.due_date).days,
                }
            )
        tasks_by_user[t.user_id].append(t)

    seven_days_ago = utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == "done", Task.updated_at >= seven_days_ago
    ).count()

    users = User.query.all()
    user_stats = []
    for u in users:
        user_tasks = tasks_by_user.get(u.id, [])
        total = len(user_tasks)
        completed = sum(1 for t in user_tasks if t.status == "done")
        user_stats.append(
            {
                "user_id": u.id,
                "user_name": u.name,
                "total_tasks": total,
                "completed_tasks": completed,
                "completion_rate": round((completed / total) * 100, 2) if total > 0 else 0,
            }
        )

    report = {
        "generated_at": str(utcnow()),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": total_users,
            "total_categories": total_categories,
        },
        "tasks_by_status": {
            "pending": pending,
            "in_progress": in_progress,
            "done": done,
            "cancelled": cancelled,
        },
        "tasks_by_priority": {
            "critical": p1,
            "high": p2,
            "medium": p3,
            "low": p4,
            "minimal": p5,
        },
        "overdue": {"count": overdue_count, "tasks": overdue_list},
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }

    return jsonify(report), 200


def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()

    total = len(tasks)
    done = sum(1 for t in tasks if t.status == "done")
    pending = sum(1 for t in tasks if t.status == "pending")
    in_progress = sum(1 for t in tasks if t.status == "in_progress")
    cancelled = sum(1 for t in tasks if t.status == "cancelled")
    overdue = sum(1 for t in tasks if t.is_overdue())
    high_priority = sum(1 for t in tasks if t.priority <= 2)

    report = {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "cancelled": cancelled,
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
        },
    }
    return jsonify(report), 200
