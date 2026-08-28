import logging

from flask import Flask, jsonify
from flask_cors import CORS

from config.settings import Settings
from database import init_app as init_db
from middlewares.error_handler import register_error_handlers
from routes.produto_routes import produto_bp
from routes.usuario_routes import usuario_bp
from routes.pedido_routes import pedido_bp
from routes.admin_routes import admin_bp

logging.basicConfig(
    level=logging.DEBUG if Settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Settings.SECRET_KEY
    app.config["DEBUG"] = Settings.DEBUG

    CORS(app, origins=Settings.CORS_ORIGINS)

    init_db(app)
    register_error_handlers(app)

    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        return jsonify(
            {
                "mensagem": "Bem-vindo à API da Loja",
                "versao": "1.0.0",
                "endpoints": {
                    "produtos": "/produtos",
                    "usuarios": "/usuarios",
                    "pedidos": "/pedidos",
                    "login": "/login",
                    "relatorios": "/relatorios/vendas",
                    "health": "/health",
                },
            }
        )

    return app


if __name__ == "__main__":
    app = create_app()

    logger.info("=" * 50)
    logger.info("SERVIDOR INICIADO")
    logger.info("Rodando em http://localhost:%d", Settings.PORT)
    logger.info("=" * 50)

    app.run(host="0.0.0.0", port=Settings.PORT, debug=Settings.DEBUG)
