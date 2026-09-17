"""WSGI entry point.

Importing this module builds the application, so keep it free of anything the
test suite needs — tests import `create_app` from app_factory directly.
"""

from app_factory import create_app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=app.config["DEBUG"])
