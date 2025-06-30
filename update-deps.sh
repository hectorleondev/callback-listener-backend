#!/bin/bash

# Update Backend Dependencies Script
echo "🔄 Updating CallbackListener Backend Dependencies"

# Check if running from the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "cd /Users/payorayo/AI_PROJECTS/callback_listener/backend"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Install/update dependencies
echo "📥 Installing updated dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies updated successfully!"
echo ""
echo "🚀 You can now start the server and access:"
echo "   📊 Swagger UI: http://localhost:5001/docs"
echo "   📋 OpenAPI YAML: http://localhost:5001/openapi.yaml"
echo "   📋 OpenAPI JSON: http://localhost:5001/openapi.json"
echo ""
echo "Start the server with: python run.py"
