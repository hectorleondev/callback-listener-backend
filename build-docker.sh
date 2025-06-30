#!/bin/bash

# Backend Docker Build Script
echo "🐳 Building Backend Docker Image"

# Set default values
IMAGE_NAME="callback-listener-backend"
TAG="latest"
DATABASE_URL="sqlite:///callback_listener.db"
SECRET_KEY="docker-secret-key-$(date +%s)"

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
    --tag)
      TAG="$2"
      shift 2
      ;;
    --name)
      IMAGE_NAME="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --database-url URL   Database URL (default: sqlite:///callback_listener.db)"
      echo "  --secret-key KEY     Flask secret key (default: auto-generated)"
      echo "  --tag TAG            Docker image tag (default: latest)"
      echo "  --name NAME          Docker image name (default: callback-listener-backend)"
      echo "  -h, --help           Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

echo "🔧 Build Configuration:"
echo "   Image Name: $IMAGE_NAME:$TAG"
echo "   Database URL: $DATABASE_URL"
echo "   Secret Key: ${SECRET_KEY:0:20}..."
echo ""

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Dockerfile not found. Make sure you're in the backend directory."
    exit 1
fi

# Build the Docker image
echo "🏗️  Building Docker image..."
docker build \
  --build-arg DATABASE_URL="$DATABASE_URL" \
  --build-arg SECRET_KEY="$SECRET_KEY" \
  -t "$IMAGE_NAME:$TAG" \
  .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "🚀 To run the container:"
    echo "   docker run -p 5000:5000 $IMAGE_NAME:$TAG"
    echo ""
    echo "🐳 To run with docker-compose:"
    echo "   DATABASE_URL=$DATABASE_URL docker-compose up"
    echo ""
    echo "📊 Image details:"
    docker images "$IMAGE_NAME:$TAG" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
else
    echo ""
    echo "❌ Build failed!"
    exit 1
fi