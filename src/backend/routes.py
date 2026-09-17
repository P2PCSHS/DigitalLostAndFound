from datetime import datetime, timezone

from better_profanity import profanity
from flask import Blueprint, current_app, jsonify, request

from extensions import db
from models import Item

profanity.load_censor_words()

MAX_DESCRIPTION_LENGTH = 200

bp = Blueprint("main", __name__)


def _commit():
    """Commit, leaving the session usable if the write fails."""
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


@bp.route("/")
def index():
    return current_app.send_static_file("index.html")


@bp.route("/health", methods=["GET"])
def get_health():
    # Touch the database so the check fails when storage is unreachable.
    db.session.execute(db.text("SELECT 1"))
    return {"status": "ok"}, 200


@bp.route("/items", methods=["GET"])
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


@bp.route("/items", methods=["POST"])
def add_item():
    data = request.get_json(silent=True) or {}

    if not all(key in data for key in ("type", "description")):
        return jsonify({"error": "Missing required fields"}), 400

    if not isinstance(data["type"], str) or not isinstance(data["description"], str):
        return jsonify({"error": "Fields must be text"}), 400

    if profanity.contains_profanity(data["description"]):
        return jsonify({"error": "Inappropriate language is not allowed"}), 400

    if len(data["description"]) > MAX_DESCRIPTION_LENGTH:
        return jsonify(
            {"error": f"Description must be {MAX_DESCRIPTION_LENGTH} characters or less"}
        ), 400

    item = Item(type=data["type"], description=data["description"])
    db.session.add(item)
    _commit()

    return jsonify(item.to_dict()), 201


@bp.route("/items/<int:item_id>/claim", methods=["POST"])
def claim_item(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    if item.claimed_at is not None:
        return jsonify({"error": "Item already claimed"}), 409

    item.claimed_at = datetime.now(timezone.utc)
    _commit()
    return jsonify(item.to_dict()), 200
