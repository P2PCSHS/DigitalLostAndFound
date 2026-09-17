"""WSGI entry point.

Importing this module builds the application but does NOT touch the database
schema — that is init_db()'s job, and the container entrypoint runs it once
before gunicorn forks its workers.
"""

from app_factory import create_app, init_db

app = create_app()


if __name__ == "__main__":
    # Convenience for `python run.py`; the container calls init_db separately.
    init_db(app)
    app.run(host="0.0.0.0", port=8000, debug=app.config["DEBUG"])
