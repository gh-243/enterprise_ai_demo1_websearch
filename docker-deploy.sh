#!/bin/bash
# Docker deployment script for AI Chatbot

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    print_warning ".env file not found"
    if [ -f .env.docker.example ]; then
        print_status "Creating .env from .env.docker.example"
        cp .env.docker.example .env
        print_warning "Please edit .env file and add your API keys before continuing"
        echo ""
        echo "Required variables:"
        echo "  - OPENAI_API_KEY (required)"
        echo "  - ANTHROPIC_API_KEY (optional)"
        echo ""
        read -p "Press Enter after you've updated .env file..."
    else
        print_error "No .env.docker.example file found"
        exit 1
    fi
fi

# Validate required environment variables
print_status "Validating environment variables..."
source .env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    print_error "OPENAI_API_KEY is not set in .env file"
    exit 1
fi

print_success "Environment variables validated"

# Build the Docker image
print_status "Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Start the containers
print_status "Starting containers..."
docker-compose up -d

if [ $? -eq 0 ]; then
    print_success "Containers started successfully"
else
    print_error "Failed to start containers"
    exit 1
fi

# Wait for application to be ready
print_status "Waiting for application to be ready..."
sleep 5

# Check health
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Application is healthy and running!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        print_error "Application failed to start properly"
        echo ""
        echo "Check logs with: docker-compose logs chatbot"
        exit 1
    fi
    echo "Waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
done

# Show status
echo ""
print_success "================================"
print_success "AI Chatbot is now running!"
print_success "================================"
echo ""
echo "🌐 Web UI:        http://localhost:8000"
echo "📚 API Docs:      http://localhost:8000/docs"
echo "❤️  Health Check: http://localhost:8000/health"
echo "💰 Cost Tracking: http://localhost:8000/v1/costs/latest"
echo ""
echo "📋 Useful commands:"
echo "  View logs:      docker-compose logs -f chatbot"
echo "  Stop:           docker-compose stop"
echo "  Restart:        docker-compose restart"
echo "  Stop & Remove:  docker-compose down"
echo "  Rebuild:        docker-compose up -d --build"
echo ""
print_status "Opening web UI in browser..."
sleep 2

# Try to open browser (works on macOS, Linux, and Windows WSL)
if command -v open &> /dev/null; then
    open http://localhost:8000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000
elif command -v start &> /dev/null; then
    start http://localhost:8000
fi
