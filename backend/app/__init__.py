from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError
from flask_migrate import Migrate

from .config import Config
from .models import db
from .routes.admin_routes import admin_bp
from .routes.candidate_routes import candidate_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Initialize Extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app, supports_credentials=True, origins="*")
    jwt = JWTManager(app)

    # ✅ Register Blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(candidate_bp, url_prefix='/candidate')

    # ✅ Error Handlers
    @app.errorhandler(NoAuthorizationError)
    def handle_missing_token(e):
        return jsonify({'error': 'Token is missing or expired.'}), 401

    @app.errorhandler(JWTDecodeError)
    def handle_invalid_token(e):
        return jsonify({'error': 'Invalid token format.'}), 401

    # ✅ Optional: Create DB Tables (for dev only)
    with app.app_context():
        db.create_all()

    return app
