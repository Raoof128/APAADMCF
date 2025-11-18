#!/bin/bash
# Run tests for ADM Compliance Framework

set -e

echo "🧪 Running ADM Compliance Framework Tests"
echo "==========================================="

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Run linting
echo ""
echo "🔍 Running flake8..."
flake8 app --max-line-length=120 --exclude=__pycache__,venv || true

# Run type checking
echo ""
echo "🔍 Running mypy..."
mypy app --ignore-missing-imports || true

# Run tests
echo ""
echo "🧪 Running pytest..."
export DATABASE_URL="sqlite:///:memory:"
export SECRET_KEY="test-secret-key"
pytest tests/ -v --cov=app --cov-report=term-missing

echo ""
echo "✅ All tests completed!"
