"""Swagger UI service for API documentation."""

import os
import yaml
from flask import current_app
from flask_restx import Api, Resource, Namespace


def create_swagger_api(app):
    """Create and configure Swagger API."""
    
    # Load OpenAPI specification
    openapi_file_path = os.path.join(
        current_app.root_path, '..', 'openapi.yaml'
    )
    
    openapi_spec = {}
    if os.path.exists(openapi_file_path):
        with open(openapi_file_path, 'r') as f:
            openapi_spec = yaml.safe_load(f)
    
    # Create Flask-RESTX API with OpenAPI spec info
    api = Api(
        app,
        version=openapi_spec.get('info', {}).get('version', '1.0.0'),
        title=openapi_spec.get('info', {}).get('title', 'CallbackListener API'),
        description=openapi_spec.get('info', {}).get('description', 
                   'A webhook capturing service API'),
        doc='/docs/',  # Swagger UI will be available at /docs/
        prefix='',
        contact=openapi_spec.get('info', {}).get('contact', {}),
        license=openapi_spec.get('info', {}).get('license', {}),
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Bearer token authentication'
            }
        },
        security='Bearer'
    )
    
    return api


def setup_swagger_docs(api):
    """Set up Swagger documentation namespaces."""
    
    # Create namespaces for different API groups
    paths_ns = Namespace('paths', description='Webhook path management operations')
    webhooks_ns = Namespace('webhooks', description='Webhook request capturing endpoints')
    health_ns = Namespace('health', description='Health check and monitoring endpoints')
    
    # Add namespaces to API
    api.add_namespace(paths_ns, path='/api')
    api.add_namespace(webhooks_ns, path='/webhook')
    api.add_namespace(health_ns, path='/health')
    
    return {
        'paths': paths_ns,
        'webhooks': webhooks_ns,
        'health': health_ns
    }
