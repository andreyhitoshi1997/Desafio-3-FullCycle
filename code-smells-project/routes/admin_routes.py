from flask import Blueprint

from controllers import admin_controller
from middlewares.auth import require_admin_token

admin_bp = Blueprint("admin", __name__)

admin_bp.add_url_rule(
    "/health", "health_check", admin_controller.health_check, methods=["GET"]
)
admin_bp.add_url_rule(
    "/admin/reset-db",
    "reset_database",
    require_admin_token(admin_controller.reset_database),
    methods=["POST"],
)
