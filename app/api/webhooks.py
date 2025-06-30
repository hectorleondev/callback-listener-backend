"""Webhook blueprint for capturing HTTP requests."""

import structlog
from flask import Blueprint, jsonify, request

from app.models.path import Path
from app.models.request import Request

logger = structlog.get_logger()
webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.route(
    "/<string:path_id>",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)
def capture_webhook(path_id):
    """Capture any HTTP request to a webhook path."""
    try:
        # Find the path
        path = Path.find_by_path_id(path_id)
        if not path:
            logger.warning("Webhook request to non-existent path", path_id=path_id)
            return jsonify({"success": False, "error": "Webhook path not found"}), 404

        # Create request record
        captured_request = Request.create_from_flask_request(request, path)

        logger.info(
            "Webhook request captured",
            path_id=path_id,
            method=request.method,
            request_id=str(captured_request.id),
            ip_address=captured_request.ip_address,
            user_agent=captured_request.user_agent[:100]
            if captured_request.user_agent
            else None,
        )

        # Return success response
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Request captured successfully",
                    "data": {
                        "request_id": str(captured_request.id),
                        "timestamp": captured_request.timestamp.isoformat(),
                        "method": captured_request.method,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(
            "Error capturing webhook request",
            path_id=path_id,
            method=request.method,
            error=str(e),
            exc_info=True,
        )
        return jsonify({"success": False, "error": "Failed to capture request"}), 500


@webhooks_bp.errorhandler(404)
def webhook_not_found(error):
    """Handle 404 errors for webhook routes."""
    return jsonify({"success": False, "error": "Webhook path not found"}), 404


@webhooks_bp.errorhandler(413)
def payload_too_large(error):
    """Handle payload too large errors."""
    return jsonify({"success": False, "error": "Request payload too large"}), 413


@webhooks_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error("Internal server error in webhook", error=str(error))
    return jsonify({"success": False, "error": "Internal server error"}), 500
