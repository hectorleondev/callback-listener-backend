"""Flask application entry point."""

import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
