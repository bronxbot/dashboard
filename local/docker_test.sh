#!/bin/bash
# Docker-based testing script for Dashboard

echo "🐳 Running Dashboard with Docker..."

# Get the project root and local directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if .env file exists
if [ ! -f "$LOCAL_DIR/.env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and fill in your credentials:"
    echo "  cp $LOCAL_DIR/.env.example $LOCAL_DIR/.env"
    echo "  # Then edit $LOCAL_DIR/.env with your settings"
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please install Docker from: https://docker.com"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed or not in PATH"
    echo "Please install Docker Compose"
    exit 1
fi

# Load environment variables for Docker
echo "⚙️  Loading environment variables..."
export $(cat "$LOCAL_DIR/.env" | grep -v '^#' | grep -v '^$' | xargs)

# Change to project root
cd "$PROJECT_ROOT"

echo ""
echo "🔧 Starting services with Docker Compose..."
echo "This will start:"
echo "  - MongoDB (database)"
echo "  - Redis (session storage)"
echo "  - Dashboard (web application)"
echo ""

# Run with Docker Compose
docker-compose -f "$LOCAL_DIR/docker-compose.test.yml" up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Services started successfully!"
    echo ""
    echo "🌐 Dashboard is running at: http://localhost:5000"
    echo "🗄️  MongoDB is available at: localhost:27017"
    echo "🔴 Redis is available at: localhost:6379"
    echo ""
    echo "📊 To check service status:"
    echo "  docker-compose -f $LOCAL_DIR/docker-compose.test.yml ps"
    echo ""
    echo "📝 To view logs:"
    echo "  docker-compose -f $LOCAL_DIR/docker-compose.test.yml logs -f"
    echo ""
    echo "🛑 To stop all services:"
    echo "  docker-compose -f $LOCAL_DIR/docker-compose.test.yml down"
    echo ""
    echo "🧹 To stop and remove volumes:"
    echo "  docker-compose -f $LOCAL_DIR/docker-compose.test.yml down -v"
else
    echo ""
    echo "❌ Failed to start services!"
    echo "Check the error messages above and try again."
    exit 1
fi
