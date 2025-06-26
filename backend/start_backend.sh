#!/bin/bash

# WageLift Backend Startup Script
# This script ensures the backend starts reliably every time

set -e  # Exit on any error

echo "🚀 Starting WageLift Backend..."

# Navigate to backend directory
cd "$(dirname "$0")"
BACKEND_DIR="$(pwd)"

echo "📁 Backend directory: $BACKEND_DIR"

# Check if we're in the right directory
if [ ! -f "simple_main.py" ]; then
    echo "❌ Error: simple_main.py not found. Are you in the backend directory?"
    exit 1
fi

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn.*simple_main" || true
pkill -f "python.*simple_main" || true
sleep 2

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check Python version
echo "🐍 Python version: $(python --version)"

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-ultra-minimal.txt

# Verify imports work
echo "✅ Verifying imports..."
python -c "import simple_main; print('✅ simple_main imported successfully')"

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is in use. Killing processes..."
    lsof -ti:8000 | xargs kill -9 || true
    sleep 2
fi

# Start the server
echo "🌟 Starting uvicorn server..."
echo "📍 Backend will be available at: http://localhost:8000"
echo "🔍 Health check: http://localhost:8000/health"
echo ""

# Start with proper error handling
exec uvicorn simple_main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    --access-log