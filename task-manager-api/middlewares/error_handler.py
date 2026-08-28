import logging

from flask import jsonify
from marshmallow import ValidationError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({"error": "Dados inválidos", "details": e.messages}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Método não permitido"}), 405

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception("Unhandled exception: %s", e)
        return jsonify({"error": "Erro interno"}), 500
