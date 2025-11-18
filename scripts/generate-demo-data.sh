#!/bin/bash
# Generate synthetic demo data for ADM Compliance Framework

set -e

echo "📊 Generating Demo Data"
echo "======================="

cd demo/scripts

# Check if virtual environment exists
if [ ! -d "../../backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd ../../backend
    python3 -m venv venv
    cd ../../demo/scripts
fi

# Activate virtual environment
source ../../backend/venv/bin/activate

# Install requirements
echo "📦 Installing dependencies..."
pip install -q pandas numpy scipy

# Generate data
echo ""
echo "🔄 Generating synthetic datasets..."
python generate_synthetic_data.py

echo ""
echo "✅ Demo data generated successfully!"
echo "📁 Files created in demo/datasets/"
