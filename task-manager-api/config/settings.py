import os
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
    PORT = int(os.environ.get("PORT", "5000"))

    JWT_EXP_HOURS = int(os.environ.get("JWT_EXP_HOURS", "8"))

    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")


if Settings.SECRET_KEY == "dev-only-change-me-in-production":
    logger.warning(
        "SECRET_KEY using default dev value — set SECRET_KEY env var for production"
    )
