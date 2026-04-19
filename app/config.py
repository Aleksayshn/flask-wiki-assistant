"""
Application configuration.

Configuration values are loaded from environment variables with safe
defaults for local development.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv


load_dotenv()


def _to_bool(value: str, default: bool = False) -> bool:
    """Convert a string environment value into a boolean."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Central configuration object for the Flask application."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "8888"))

    MYSQL_CACHE_ENABLED = _to_bool(os.getenv("MYSQL_CACHE_ENABLED"), default=False)
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "wiki_cache")
    MYSQL_USER = os.getenv("MYSQL_USER", "wiki_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "wiki_password")

    REMOTE_EXECUTION_ENABLED = _to_bool(
        os.getenv("REMOTE_EXECUTION_ENABLED"), default=False
    )

    # Remote EC2 settings for the distributed search step of the assignment.
    # These values are loaded from environment variables so that credentials
    # and server details are never hardcoded into the repository.
    EC2_HOST = os.getenv("EC2_HOST", "")
    EC2_PORT = int(os.getenv("EC2_PORT", "22"))
    EC2_USERNAME = os.getenv("EC2_USERNAME", "")
    EC2_KEY_PATH = os.getenv("EC2_KEY_PATH", "")
    EC2_WIKI_SCRIPT_PATH = os.getenv("EC2_WIKI_SCRIPT_PATH", "")
