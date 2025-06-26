#!/bin/bash

# WageLift Master Startup Script
# Starts both backend and frontend servers reliably

set -e

echo "🚀 WageLift Master Startup Script"
echo "=================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Project root: $SCRIPT_DIR"

# Kill any existing processes first
echo ""
echo "🧹 Cleaning up all existing processes..."
pkill -f "uvicorn" || true
pkill -f "next" || true
pkill -f "node.*next" || true
sleep 3

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is in use. Killing processes..."
        lsof -ti:$port | xargs kill -9 || true
        sleep 2
    fi
}

# Check and clear ports
check_port 8000
check_port 3000

echo ""
echo "🔧 Starting Backend Server..."
echo "=============================="

# Start backend in background
cd "$SCRIPT_DIR/backend"
if [ ! -f "start_backend.sh" ]; then
    echo "❌ Backend startup script not found!"
    exit 1
fi

# Start backend in background and capture PID
nohup ./start_backend.sh > backend.log 2>&1 &
BACKEND_PID=$!
echo "🔗 Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running on http://localhost:8000"
        break
    else
        echo "⏳ Attempt $i/10: Backend not ready yet..."
        sleep 2
    fi
    
    if [ $i -eq 10 ]; then
        echo "❌ Backend failed to start after 20 seconds"
        echo "📄 Backend logs:"
        tail -20 backend.log
        exit 1
    fi
done

echo ""
echo "🌐 Starting Frontend Server..."
echo "==============================="

# Start frontend
cd "$SCRIPT_DIR/frontend"
if [ ! -f "start_frontend.sh" ]; then
    echo "❌ Frontend startup script not found!"
    exit 1
fi

# Start frontend in background and capture PID
nohup ./start_frontend.sh > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "🔗 Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 8

# Test frontend
for i in {1..15}; do
    if curl -s -I http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is running on http://localhost:3000"
        break
    else
        echo "⏳ Attempt $i/15: Frontend not ready yet..."
        sleep 3
    fi
    
    if [ $i -eq 15 ]; then
        echo "❌ Frontend failed to start after 45 seconds"
        echo "📄 Frontend logs:"
        tail -20 frontend.log
        exit 1
    fi
done

echo ""
echo "🎉 WageLift is now running!"
echo "=========================="
echo "🔗 Backend:  http://localhost:8000"
echo "🔗 Frontend: http://localhost:3000"
echo "🔍 Health:   http://localhost:8000/health"
echo ""
echo "📊 Process Information:"
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "📄 To view logs:"
echo "Backend:  tail -f $SCRIPT_DIR/backend/backend.log"
echo "Frontend: tail -f $SCRIPT_DIR/frontend/frontend.log"
echo ""
echo "🛑 To stop all servers:"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo "or run: pkill -f 'uvicorn|next'"
echo ""
echo "✨ Happy coding!"

# Keep script running to monitor processes
echo "🔍 Monitoring servers... (Press Ctrl+C to stop monitoring)"
while true; do
    sleep 10
    
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "⚠️  Backend process died! PID: $BACKEND_PID"
        break
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚠️  Frontend process died! PID: $FRONTEND_PID"
        break
    fi
    
    # Quick health check
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "⚠️  Backend health check failed!"
    fi
    
    if ! curl -s -I http://localhost:3000 > /dev/null 2>&1; then
        echo "⚠️  Frontend health check failed!"
    fi
done