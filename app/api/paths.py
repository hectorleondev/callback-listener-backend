"""API blueprint for path management."""

import structlog
from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields

from app.models.path import Path
from app.models.request import Request

logger = structlog.get_logger()
paths_bp = Blueprint("paths", __name__)


class CreatePathSchema(Schema):
    """Schema for creating a new path."""

    path_id = fields.Str(required=False, allow_none=True)


class PathResponseSchema(Schema):
    """Schema for path response."""

    id = fields.Str(required=True)
    path_id = fields.Str(required=True)
    created_at = fields.Str(required=True)
    updated_at = fields.Str(required=True)
    request_count = fields.Int(required=True)


class RequestResponseSchema(Schema):
    """Schema for request response."""

    id = fields.Str(required=True)
    path_id = fields.Str(required=True)
    method = fields.Str(required=True)
    headers = fields.Dict(required=True)
    body = fields.Str(allow_none=True)
    query_params = fields.Dict(required=True)
    ip_address = fields.Str(allow_none=True)
    user_agent = fields.Str(allow_none=True)
    timestamp = fields.Str(required=True)


@paths_bp.route("/paths", methods=["GET"])
def get_all_paths():
    """Get all webhook paths."""
    try:
        paths = Path.get_all_paths()
        
        # Serialize paths
        response_schema = PathResponseSchema(many=True)
        paths_data = [path.to_dict() for path in paths]
        
        logger.info("All paths retrieved", count=len(paths_data))
        
        return (
            jsonify({"success": True, "data": response_schema.dump(paths_data)}),
            200,
        )
    
    except Exception as e:
        logger.error("Error retrieving all paths", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


@paths_bp.route("/paths/<string:path_id>", methods=["GET"])
def get_path(path_id):
    """Get a specific path by path_id."""
    try:
        path = Path.find_by_path_id(path_id)
        if not path:
            return jsonify({"success": False, "error": "Path not found"}), 404
        
        # Serialize path
        response_schema = PathResponseSchema()
        
        logger.info("Path retrieved", path_id=path_id)
        
        return (
            jsonify({"success": True, "data": response_schema.dump(path.to_dict())}),
            200,
        )
    
    except Exception as e:
        logger.error("Error retrieving path", path_id=path_id, error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


@paths_bp.route("/paths/<string:path_id>", methods=["DELETE"])
def delete_path(path_id):
    """Delete a webhook path and all its requests."""
    try:
        path = Path.find_by_path_id(path_id)
        if not path:
            return jsonify({"success": False, "error": "Path not found"}), 404
        
        # Delete the path (this should cascade delete all related requests)
        path.delete()
        
        logger.info("Path deleted", path_id=path_id)
        
        return (
            jsonify({"success": True, "message": "Path deleted successfully"}),
            200,
        )
    
    except Exception as e:
        logger.error("Error deleting path", path_id=path_id, error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


@paths_bp.route("/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        # Get basic stats
        total_paths = Path.count_all()
        all_paths = Path.get_all_paths()
        
        # Calculate stats
        total_requests = sum(path.request_count for path in all_paths)
        active_paths = len([path for path in all_paths if path.request_count > 0])
        
        # Get recent requests (last 10)
        recent_requests = Request.get_recent_requests(limit=10)
        
        # Serialize recent requests
        request_schema = RequestResponseSchema(many=True)
        recent_requests_data = [req.to_dict(include_body=False) for req in recent_requests]
        
        stats = {
            "total_webhooks": total_paths,
            "total_requests": total_requests,
            "active_webhooks": active_paths,
            "recent_requests": request_schema.dump(recent_requests_data),
        }
        
        logger.info("Dashboard stats retrieved", stats=stats)
        
        return (
            jsonify({"success": True, "data": stats}),
            200,
        )
    
    except Exception as e:
        logger.error("Error retrieving dashboard stats", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


@paths_bp.route("/paths", methods=["POST"])
def create_path():
    """Create a new webhook path."""
    try:
        # Validate request data
        schema = CreatePathSchema()
        data = schema.load(request.get_json() or {})

        # Create new path
        path = Path.create_new_path(path_id=data.get("path_id"))

        logger.info("Path created", path_id=path.path_id, id=str(path.id))

        # Return response
        response_schema = PathResponseSchema()
        return (
            jsonify({"success": True, "data": response_schema.dump(path.to_dict())}),
            201,
        )

    except ValidationError as e:
        logger.warning("Validation error creating path", errors=e.messages)
        return (
            jsonify(
                {"success": False, "error": "Validation error", "details": e.messages}
            ),
            400,
        )

    except Exception as e:
        logger.error("Error creating path", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


@paths_bp.route("/paths/<string:path_id>/logs", methods=["GET"])
def get_path_logs(path_id):
    """Get logs for a specific path."""
    try:
        # Get pagination parameters
        limit = min(int(request.args.get("limit", 100)), 1000)  # Max 1000
        offset = max(int(request.args.get("offset", 0)), 0)
        include_body = request.args.get("include_body", "true").lower() == "true"

        # Check if path exists
        path = Path.find_by_path_id(path_id)
        if not path:
            return jsonify({"success": False, "error": "Path not found"}), 404

        # Get requests
        requests = Request.get_by_path_id(path_id, limit=limit, offset=offset)

        # Serialize requests
        response_schema = RequestResponseSchema(many=True)
        requests_data = [req.to_dict(include_body=include_body) for req in requests]

        logger.info(
            "Path logs retrieved",
            path_id=path_id,
            count=len(requests_data),
            limit=limit,
            offset=offset,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "path": PathResponseSchema().dump(path.to_dict()),
                        "requests": response_schema.dump(requests_data),
                        "pagination": {
                            "limit": limit,
                            "offset": offset,
                            "total": len(path.requests) if path.requests else 0,
                        },
                    },
                }
            ),
            200,
        )

    except ValueError:
        return (
            jsonify({"success": False, "error": "Invalid pagination parameters"}),
            400,
        )

    except Exception as e:
        logger.error(
            "Error retrieving path logs", path_id=path_id, error=str(e), exc_info=True
        )
        return jsonify({"success": False, "error": "Internal server error"}), 500


@paths_bp.route("/paths/<string:path_id>/logs/<string:request_id>", methods=["GET"])
def get_specific_request(path_id, request_id):
    """Get a specific request by ID."""
    try:
        # Find the request
        req = Request.get_by_id_and_path(request_id, path_id)
        if not req:
            return jsonify({"success": False, "error": "Request not found"}), 404

        # Serialize request
        response_schema = RequestResponseSchema()

        logger.info(
            "Specific request retrieved", path_id=path_id, request_id=request_id
        )

        return (
            jsonify({"success": True, "data": response_schema.dump(req.to_dict())}),
            200,
        )

    except Exception as e:
        logger.error(
            "Error retrieving specific request",
            path_id=path_id,
            request_id=request_id,
            error=str(e),
            exc_info=True,
        )
        return jsonify({"success": False, "error": "Internal server error"}), 500


@paths_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@paths_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({"success": False, "error": "Method not allowed"}), 405
