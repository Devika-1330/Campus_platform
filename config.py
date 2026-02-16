"""Application configuration."""
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "campus-platform-dev-key-change-in-production"
    MYSQL_HOST = os.environ.get("MYSQL_HOST") or "localhost"
    MYSQL_USER = os.environ.get("MYSQL_USER") or "root"
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD") or ""
    MYSQL_DB = os.environ.get("MYSQL_DB") or "campus_platform"
    MYSQL_CURSORCLASS = "DictCursor"
