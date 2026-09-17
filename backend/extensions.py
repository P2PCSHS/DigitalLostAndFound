import sqlite3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, connection_record):
    """Apply SQLite settings that reset with every connection.

    Only per-connection settings belong here. journal_mode is deliberately not
    set: it persists in the database file, and setting it needs an exclusive
    lock, so doing it on every connect makes concurrent workers collide.
    init_db() sets it once instead.
    """
    if not isinstance(dbapi_connection, sqlite3.Connection):
        return
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
