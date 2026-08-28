import os
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me-in-production")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-admin-token")
    PORT = int(os.environ.get("PORT", "5000"))
    DB_PATH = os.environ.get(
        "DB_PATH",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "loja.db"),
    )


if Settings.SECRET_KEY == "dev-only-change-me-in-production":
    logger.warning(
        "SECRET_KEY using default dev value — set SECRET_KEY env var for production"
    )
