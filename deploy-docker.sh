#!/bin/bash

# Backend Docker Deployment Script
echo "🚀 Deploying Backend Container"

# Set default values
CONTAINER_NAME="callback-listener-backend"
IMAGE_NAME="callback-listener-backend"
TAG="latest"
PORT="5001"
DATABASE_URL="sqlite:///callback_listener.db"
SECRET_KEY="docker-secret-key-$(date +%s)"
LOG_LEVEL="INFO"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --database-url)
      DATABASE_URL="$2"
      shift 2
      ;;
    --secret-key)
      SECRET_KEY="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --tag)
      TAG="$2"
      shift 2
      ;;
    --name)
      CONTAINER_NAME="$2"
      shift 2
      ;;
    --image)
      IMAGE_NAME="$2"
      shift 2
      ;;
    --log-level)
      LOG_LEVEL="$2"
      shift 2
      ;;
    --stop)
      echo "🛑 Stopping container $CONTAINER_NAME..."
      docker stop "$CONTAINER_NAME" 2>/dev/null
      docker rm "$CONTAINER_NAME" 2>/dev/null
      echo "✅ Container stopped and removed"
      exit 0
      ;;
    --logs)
      echo "📋 Showing logs for $CONTAINER_NAME..."
      docker logs -f "$CONTAINER_NAME"
      exit 0
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --database-url URL   Database URL (default: sqlite:///callback_listener.db)"
      echo "  --secret-key KEY     Flask secret key (default: auto-generated)"
      echo "  --port PORT          Host port to bind (default: 5001)"
      echo "  --tag TAG            Docker image tag (default: latest)"
      echo "  --name NAME          Container name (default: callback-listener-backend)"
      echo "  --image IMAGE        Image name (default: callback-listener-backend)"
      echo "  --log-level LEVEL    Log level (default: INFO)"
      echo "  --stop               Stop and remove the container"
      echo "  --logs               Show container logs"
      echo "  -h, --help           Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

echo "🔧 Deployment Configuration:"
echo "   Container Name: $CONTAINER_NAME"
echo "   Image: $IMAGE_NAME:$TAG"
echo "   Port: $PORT"
echo "   Database URL: $DATABASE_URL"
echo "   Secret Key: ${SECRET_KEY:0:20}..."
echo "   Log Level: $LOG_LEVEL"
echo ""

# Check if image exists
if ! docker image inspect "$IMAGE_NAME:$TAG" >/dev/null 2>&1; then
    echo "❌ Error: Image $IMAGE_NAME:$TAG not found."
    echo "💡 Build the image first:"
    echo "   ./build-docker.sh --database-url '$DATABASE_URL'"
    exit 1
fi

# Stop existing container if running
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    echo "🛑 Stopping existing container..."
    docker stop "$CONTAINER_NAME"
fi

# Remove existing container if it exists
if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
    echo "🗑️  Removing existing container..."
    docker rm "$CONTAINER_NAME"
fi

# Create data directory for SQLite if using SQLite
if echo "$DATABASE_URL" | grep -q "sqlite"; then
    mkdir -p "$(pwd)/data"
    echo "📁 Created data directory for SQLite database"
fi

# Run the new container
echo "🐳 Starting new container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$PORT:5000" \
  -e FLASK_ENV=production \
  -e FLASK_HOST=0.0.0.0 \
  -e FLASK_PORT=5000 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e SECRET_KEY="$SECRET_KEY" \
  -e LOG_LEVEL="$LOG_LEVEL" \
  -v "$(pwd)/data:/app/data" \
  --restart unless-stopped \
  "$IMAGE_NAME:$TAG"

# Check if container started successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Container started successfully!"
    echo ""
    echo "⏳ Waiting for container to be ready..."
    sleep 5
    
    # Check if container is still running
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        echo "🌐 Backend URL: http://localhost:$PORT"
        echo "🏥 Health Check: http://localhost:$PORT/health/"
        echo "📊 Container Status:"
        docker ps --filter name="$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "📋 To view logs: docker logs -f $CONTAINER_NAME"
        echo "🛑 To stop: docker stop $CONTAINER_NAME"
        echo ""
        echo "🎉 Backend is now running in production mode!"
    else
        echo "❌ Container failed to stay running. Check logs:"
        docker logs "$CONTAINER_NAME"
        exit 1
    fi
else
    echo ""
    echo "❌ Failed to start container!"
    exit 1
fi