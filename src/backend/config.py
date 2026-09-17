import os
from pathlib import Path

from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent
load_dotenv(basedir / ".env")

DEFAULT_DATA_DIR = basedir / "data"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-not-secret-fallback-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLite serialises writes, so concurrent gunicorn workers will collide.
    # Wait for the other writer rather than raising "database is locked".
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"timeout": 15}}

    @classmethod
    def validate(cls):
        """Raise if this config is unusable. Overridden where it matters."""


class DevelopmentConfig(Config):
    DEBUG = True
    DATA_DIR = Path(os.environ.get("DATA_DIR") or DEFAULT_DATA_DIR)
    # basedir is absolute, so "sqlite:///" + an absolute path gives the
    # four-slash form SQLAlchemy expects for absolute SQLite paths.
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or f"sqlite:///{DATA_DIR / 'dev.db'}"
    )


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # config attribute -> the environment variable that supplies it
    _REQUIRED = {
        "SECRET_KEY": "SECRET_KEY",
        "SQLALCHEMY_DATABASE_URI": "DATABASE_URL",
    }

    @classmethod
    def validate(cls):
        missing = sorted(
            env_name
            for attr, env_name in cls._REQUIRED.items()
            if not getattr(cls, attr)
        )
        if missing:
            raise RuntimeError(
                "Missing required production environment variables: "
                + ", ".join(missing)
            )


class TestConfig(Config):
    TESTING = True
    DEBUG = False
    # Each app instance gets its own in-memory database, so tests are isolated
    # and leave nothing on disk.
    SQLALCHEMY_DATABASE_URI = "sqlite://"
