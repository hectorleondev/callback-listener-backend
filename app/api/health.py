"""Health check blueprint."""

import structlog
from flask import Blueprint, jsonify
from sqlalchemy import text

from app import db

logger = structlog.get_logger()
health_bp = Blueprint("health", __name__)


@health_bp.route("/", methods=["GET"])
def health_check():
    """Basic health check endpoint."""
    return jsonify({"status": "healthy", "service": "callback-listener-backend"}), 200


@health_bp.route("/ready", methods=["GET"])
def readiness_check():
    """Readiness check including database connectivity."""
    try:
        # Test database connection
        db.session.execute(text("SELECT 1"))

        return (
            jsonify(
                {
                    "status": "ready",
                    "service": "callback-listener-backend",
                    "database": "connected",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return (
            jsonify(
                {
                    "status": "not ready",
                    "service": "callback-listener-backend",
                    "database": "disconnected",
                    "error": str(e),
                }
            ),
            503,
        )


@health_bp.route("/live", methods=["GET"])
def liveness_check():
    """Liveness check for basic application health."""
    return jsonify({"status": "alive", "service": "callback-listener-backend"}), 200
