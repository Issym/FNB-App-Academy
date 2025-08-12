import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from config import Config
from db import db
from auth import bp as auth_bp
from contacts import bp as contacts_bp

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(contacts_bp)

    # Health check
    @app.get("/")
    def index():
        return jsonify({"status": "ok", "app": "Contact Book API"})

    # Error handlers (friendly JSON)
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "bad request"}), 400

    return app

if __name__ == "__main__":
    app = create_app()
    host = app.config.get("HOST", "127.0.0.1")
    port = app.config.get("PORT", 5000)
    with app.app_context():
        # Ensure DB exists (tables must already be created by scripts/init_db.py)
        pass
    app.run(host=host, port=port, debug=True)
