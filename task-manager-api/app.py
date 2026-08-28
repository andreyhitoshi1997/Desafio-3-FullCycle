import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from routes.category_routes import category_bp
from utils.helpers import utcnow

logging.basicConfig(
    level=logging.DEBUG if Settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = Settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = Settings.SECRET_KEY

CORS(app, origins=Settings.CORS_ORIGINS)
db.init_app(app)

register_error_handlers(app)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)
app.register_blueprint(category_bp)


@app.route('/health')
def health():
    return {'status': 'ok', 'timestamp': str(utcnow())}


@app.route('/')
def index():
    return {'message': 'Task Manager API', 'version': '1.0'}


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("SERVIDOR INICIADO")
    logger.info("Rodando em http://localhost:%d", Settings.PORT)
    logger.info("=" * 50)
    app.run(debug=Settings.DEBUG, host='0.0.0.0', port=Settings.PORT)
