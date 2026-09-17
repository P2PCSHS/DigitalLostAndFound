import os
from pathlib import Path

from better_profanity import profanity
from config import DevelopmentConfig, ProductionConfig
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from models import Item

profanity.load_censor_words()
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
from datetime import datetime, timezone

from extensions import db

app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
basedir = Path(__file__).resolve().parent
load_dotenv(basedir / ".env")
environment = os.getenv("FLASK_ENV", "development")
if environment == "production":
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/health", methods=["GET"])
def get_health():
    return {"status": "ok"}, 200


@app.route("/items", methods=["GET"])
def get_items():
    status = request.args.get("status", "unclaimed")
    items = db.select(Item)
    if status == "unclaimed":
        items = items.where(Item.claimed_at.is_(None))
    elif status == "claimed":
        items = items.where(Item.claimed_at.is_not(None))
    elif status != "all":
        return jsonify({"error": "Invalid status"}), 400

    rows = db.session.scalars(items.order_by(Item.created_at.desc())).all()
    return jsonify([i.to_dict() for i in rows]), 200


@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json(silent=True) or {}

    if not all(key in data for key in ("type", "description")):
        return jsonify({"error": "Missing required fields"}), 400

    if profanity.contains_profanity(data["description"]):
        return jsonify({"error": "Inappropriate language is not allowed"}), 400

    if len(data["description"]) > 200:
        return jsonify({"error": "Description must be less than 200 characters"}), 400

    item = Item(type=data["type"], description=data["description"])

    db.session.add(item)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


    return jsonify(item.to_dict()), 201


@app.route("/items/<int:item_id>/claim", methods=["POST"])
def claim_item(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    if item.claimed_at is not None:
        return jsonify({"error": "Item already claimed"}), 409

    item.claimed_at = datetime.now(timezone.utc)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return jsonify(item.to_dict()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
