#!/bin/bash
# Development startup script for ADM Compliance Framework

set -e

echo "🚀 Starting ADM Compliance Framework (Development Mode)"
echo "========================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please review backend/.env and update with your configuration"
fi

# Build and start services
echo ""
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d postgres redis

echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

echo ""
echo "🗄️  Initializing database..."
docker-compose exec -T postgres psql -U postgres -d adm_compliance -f /docker-entrypoint-initdb.d/01-schema.sql || true

echo ""
echo "🚀 Starting backend and frontend..."
docker-compose up -d backend frontend

echo ""
echo "✅ ADM Compliance Framework is starting!"
echo ""
echo "📍 Access points:"
echo "   - Frontend:  http://localhost:3000"
echo "   - Backend:   http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/api/docs"
echo "   - PgAdmin:   http://localhost:5050 (optional)"
echo ""
echo "📊 View logs with: docker-compose logs -f"
echo "🛑 Stop services with: docker-compose down"
echo ""
echo "Default login credentials:"
echo "   Email:    admin@example.gov.au"
echo "   Password: Admin123!"
echo "⚠️  CHANGE THESE IMMEDIATELY IN PRODUCTION!"
echo ""
