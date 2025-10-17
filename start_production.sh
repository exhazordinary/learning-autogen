#!/bin/bash

# Production startup script for AutoGen Research Application

set -e

echo "🚀 Starting AutoGen Research Application (Production Mode)"
echo "============================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding."
    exit 1
fi

# Load environment variables
source .env

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Determine docker compose command
if docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "📦 Pulling latest images..."
$DOCKER_COMPOSE pull

echo "🏗️  Building images..."
$DOCKER_COMPOSE build

echo "🗄️  Setting up database..."
$DOCKER_COMPOSE up -d postgres redis

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "🔄 Running database migrations..."
$DOCKER_COMPOSE run --rm backend python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"

echo "🚀 Starting all services..."
$DOCKER_COMPOSE up -d

echo ""
echo "✅ Application started successfully!"
echo "============================================================"
echo ""
echo "🔗 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5001"
echo "   API Documentation: http://localhost:5001/api/docs"
echo ""
echo "📊 Monitor services:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
