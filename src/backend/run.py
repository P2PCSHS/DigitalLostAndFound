from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from better_profanity import profanity
import os
from pathlib import Path
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig
import models
profanity.load_censor_words()
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
from extensions import db

app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
CORS(app)
basedir = Path(__file__).resolve().parent
load_dotenv(basedir / ".env")
environment = os.getenv("FLASK_ENV", "development")
if (environment == "production"):
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

db.init_app(app)
with app.app_context():
    db.create_all()

items = []

@app.route("/")
def index():
    return app.send_static_file("index.html")

def serve_css():
    return send_file("style.css")

def serve_js():
    return send_file("script.js")

@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(items), 200

@app.route("/items", methods=["POST"])
def add_item():
    try:
        data = request.get_json()

        if not all(key in data for key in ["type", "description"]):
            return jsonify({"error": "Missing required fields"}), 400

        if profanity.contains_profanity(data["description"]):
            return jsonify({"error": "Inappropriate language is not allowed"}), 400

        item = {
            "id": len(items) + 1,
            "type": data["type"],
            "description": data["description"]
        }

        items.append(item)
        return jsonify(item), 201

    except Exception as e:
        return jsonify({"error": "Invalid request", "details": str(e)}), 400

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global items
    item_to_delete = next((item for item in items if item["id"] == item_id), None)
    if not item_to_delete:
        return jsonify({"error": "Item not found"}), 404

    items = [item for item in items if item["id"] != item_id]
    return jsonify({"message": "Item deleted successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)