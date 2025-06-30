"""API documentation endpoints."""

import os
import yaml
from flask import Blueprint, jsonify, render_template_string, current_app, send_file

docs_bp = Blueprint('docs', __name__)


@docs_bp.route('/docs')
def swagger_ui():
    """Serve Swagger UI for API documentation."""
    # Simple Swagger UI HTML template
    swagger_ui_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CallbackListener API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
        <style>
            html {
                box-sizing: border-box;
                overflow: -moz-scrollbars-vertical;
                overflow-y: scroll;
            }
            *, *:before, *:after {
                box-sizing: inherit;
            }
            body {
                margin:0;
                background: #fafafa;
            }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
        <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-standalone-preset.js"></script>
        <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/openapi.yaml',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            })
        }
        </script>
    </body>
    </html>
    '''
    return render_template_string(swagger_ui_template)


@docs_bp.route('/openapi.yaml')
def openapi_yaml():
    """Serve OpenAPI specification in YAML format."""
    openapi_file_path = os.path.join(
        current_app.root_path, '..', 'openapi.yaml'
    )
    
    if os.path.exists(openapi_file_path):
        return send_file(openapi_file_path, mimetype='application/x-yaml')
    else:
        return jsonify({"error": "OpenAPI specification not found"}), 404


@docs_bp.route('/openapi.json')
def openapi_json():
    """Serve OpenAPI specification in JSON format."""
    openapi_file_path = os.path.join(
        current_app.root_path, '..', 'openapi.yaml'
    )
    
    if os.path.exists(openapi_file_path):
        with open(openapi_file_path, 'r') as f:
            openapi_spec = yaml.safe_load(f)
        return jsonify(openapi_spec)
    else:
        return jsonify({"error": "OpenAPI specification not found"}), 404


@docs_bp.route('/api-docs')
def api_docs_redirect():
    """Redirect /api-docs to /docs for convenience."""
    from flask import redirect
    return redirect('/docs')
