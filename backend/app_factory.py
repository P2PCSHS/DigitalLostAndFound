import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy.engine import make_url

from config import DevelopmentConfig, ProductionConfig
from extensions import db
from routes import bp

basedir = Path(__file__).resolve().parent
FRONTEND = basedir.parent / "frontend"

load_dotenv(basedir / ".env")


def select_config():
    """Pick a config class from the environment."""
    environment = os.getenv("FLASK_ENV", "development")
    return ProductionConfig if environment == "production" else DevelopmentConfig


def ensure_sqlite_directory(app):
    """SQLite creates the database file but not the directory holding it."""
    url = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
    if url.drivername.startswith("sqlite") and url.database:
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)


def create_app(config=None):
    if config is None:
        config = select_config()
    # Fail at boot on missing configuration rather than at the first request.
    config.validate()

    app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
    app.config.from_object(config)

    db.init_app(app)
    ensure_sqlite_directory(app)
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app
