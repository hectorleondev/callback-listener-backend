"""Flask application factory and configuration."""

import os

import structlog
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Load configuration
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(f"app.config.{config_name.title()}Config")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Register blueprints
    from app.api.health import health_bp
    from app.api.paths import paths_bp
    from app.api.webhooks import webhooks_bp
    from app.api.docs import docs_bp

    app.register_blueprint(paths_bp, url_prefix="/api")
    app.register_blueprint(webhooks_bp, url_prefix="/webhook")
    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(docs_bp)

    # Import models to ensure they are registered with SQLAlchemy
    from app.models import path, request

    return app
