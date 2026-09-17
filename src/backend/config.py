import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent
load_dotenv(basedir / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-not-secret-fallback-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "*")

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'dev.db'}"

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN")
