#!/bin/bash

# WageLift Frontend Startup Script
# This script ensures the frontend starts reliably every time

set -e  # Exit on any error

echo "🌐 Starting WageLift Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")"
FRONTEND_DIR="$(pwd)"

echo "📁 Frontend directory: $FRONTEND_DIR"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Are you in the frontend directory?"
    exit 1
fi

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "next.*dev" || true
pkill -f "node.*next" || true
sleep 2

# Check Node.js version
echo "📦 Node.js version: $(node --version)"
echo "📦 npm version: $(npm --version)"

# Clear Next.js cache
echo "🗑️  Clearing Next.js cache..."
rm -rf .next || true
rm -rf node_modules/.cache || true

# Install dependencies
echo "📚 Installing/updating dependencies..."
npm install

# Verify critical files exist
echo "✅ Verifying project structure..."
[ -f "src/app/page.tsx" ] || { echo "❌ Missing src/app/page.tsx"; exit 1; }
[ -f "src/app/layout.tsx" ] || { echo "❌ Missing src/app/layout.tsx"; exit 1; }
[ -f "tailwind.config.js" ] || { echo "❌ Missing tailwind.config.js"; exit 1; }

# Check if port 3000 is available
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3000 is in use. Killing processes..."
    lsof -ti:3000 | xargs kill -9 || true
    sleep 2
fi

# Build check (optional - comment out for faster startup)
# echo "🔨 Running build check..."
# npm run build

# Start the development server
echo "🌟 Starting Next.js development server..."
echo "📍 Frontend will be available at: http://localhost:3000"
echo "🔄 Hot reload enabled"
echo ""

# Start with proper error handling
exec npm run dev