#!/bin/bash

# WageLift Health Check Script
# Comprehensive monitoring and diagnostics

echo "🏥 WageLift Health Check"
echo "========================"
echo "Timestamp: $(date)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Check if processes are running
echo "🔍 Process Status:"
echo "=================="

# Check backend process
if pgrep -f "uvicorn.*simple_main" > /dev/null; then
    BACKEND_PID=$(pgrep -f "uvicorn.*simple_main")
    print_status "OK" "Backend process running (PID: $BACKEND_PID)"
else
    print_status "ERROR" "Backend process not running"
fi

# Check frontend process
if pgrep -f "next.*dev" > /dev/null; then
    FRONTEND_PID=$(pgrep -f "next.*dev")
    print_status "OK" "Frontend process running (PID: $FRONTEND_PID)"
else
    print_status "ERROR" "Frontend process not running"
fi

echo ""

# Check port availability
echo "🌐 Port Status:"
echo "==============="

# Check backend port
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_status "OK" "Port 8000 (Backend) is listening"
else
    print_status "ERROR" "Port 8000 (Backend) is not listening"
fi

# Check frontend port
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_status "OK" "Port 3000 (Frontend) is listening"
else
    print_status "ERROR" "Port 3000 (Frontend) is not listening"
fi

echo ""

# HTTP Health Checks
echo "🔗 HTTP Health Checks:"
echo "======================"

# Backend health check
BACKEND_HEALTH=$(curl -s -w "%{http_code}" -o /tmp/backend_response http://localhost:8000/health 2>/dev/null)
if [ "$BACKEND_HEALTH" = "200" ]; then
    BACKEND_DATA=$(cat /tmp/backend_response)
    print_status "OK" "Backend health endpoint responding (200)"
    echo "   Response: $BACKEND_DATA"
else
    print_status "ERROR" "Backend health endpoint failed (HTTP: $BACKEND_HEALTH)"
fi

# Frontend health check
FRONTEND_HEALTH=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:3000 2>/dev/null)
if [ "$FRONTEND_HEALTH" = "200" ]; then
    print_status "OK" "Frontend responding (200)"
else
    print_status "ERROR" "Frontend failed (HTTP: $FRONTEND_HEALTH)"
fi

echo ""

# API Endpoint Tests
echo "🧪 API Endpoint Tests:"
echo "======================"

# Test backend API endpoints
endpoints=(
    "/api/test"
    "/api/user/profile"
    "/api/auth/session"
    "/api/raise-letter/templates"
)

for endpoint in "${endpoints[@]}"; do
    HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:8000$endpoint" 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        print_status "OK" "GET $endpoint"
    else
        print_status "ERROR" "GET $endpoint (HTTP: $HTTP_CODE)"
    fi
done

echo ""

# Frontend Page Tests
echo "🌐 Frontend Page Tests:"
echo "======================="

# Test critical frontend pages
pages=(
    "/"
    "/dashboard/salary"
    "/dashboard/raise-letter"
    "/dashboard/results"
)

for page in "${pages[@]}"; do
    HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:3000$page" 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        print_status "OK" "Page $page"
    else
        print_status "WARNING" "Page $page (HTTP: $HTTP_CODE)"
    fi
done

echo ""

# System Resources
echo "💻 System Resources:"
echo "===================="

# Memory usage
MEMORY_USAGE=$(free | grep '^Mem:' | awk '{printf "%.1f", $3/$2 * 100.0}')
if (( $(echo "$MEMORY_USAGE < 80" | bc -l) )); then
    print_status "OK" "Memory usage: ${MEMORY_USAGE}%"
else
    print_status "WARNING" "Memory usage: ${MEMORY_USAGE}%"
fi

# Disk usage
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_status "OK" "Disk usage: ${DISK_USAGE}%"
else
    print_status "WARNING" "Disk usage: ${DISK_USAGE}%"
fi

echo ""

# Log File Checks
echo "📄 Log File Status:"
echo "==================="

# Check backend logs
if [ -f "backend/backend.log" ]; then
    BACKEND_LOG_SIZE=$(stat -c%s backend/backend.log)
    print_status "OK" "Backend log exists (${BACKEND_LOG_SIZE} bytes)"
    
    # Check for recent errors
    if tail -20 backend/backend.log | grep -i error > /dev/null; then
        print_status "WARNING" "Recent errors found in backend log"
        echo "   Last error lines:"
        tail -20 backend/backend.log | grep -i error | tail -3 | sed 's/^/   /'
    else
        print_status "OK" "No recent errors in backend log"
    fi
else
    print_status "WARNING" "Backend log file not found"
fi

# Check frontend logs
if [ -f "frontend/frontend.log" ]; then
    FRONTEND_LOG_SIZE=$(stat -c%s frontend/frontend.log)
    print_status "OK" "Frontend log exists (${FRONTEND_LOG_SIZE} bytes)"
    
    # Check for recent errors
    if tail -20 frontend/frontend.log | grep -i -E "(error|failed)" > /dev/null; then
        print_status "WARNING" "Recent errors found in frontend log"
        echo "   Last error lines:"
        tail -20 frontend/frontend.log | grep -i -E "(error|failed)" | tail -3 | sed 's/^/   /'
    else
        print_status "OK" "No recent errors in frontend log"
    fi
else
    print_status "WARNING" "Frontend log file not found"
fi

echo ""

# Performance Test
echo "⚡ Performance Test:"
echo "==================="

# Test response times
BACKEND_TIME=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:8000/health 2>/dev/null)
FRONTEND_TIME=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:3000 2>/dev/null)

if (( $(echo "$BACKEND_TIME < 1.0" | bc -l) )); then
    print_status "OK" "Backend response time: ${BACKEND_TIME}s"
else
    print_status "WARNING" "Backend response time: ${BACKEND_TIME}s (slow)"
fi

if (( $(echo "$FRONTEND_TIME < 2.0" | bc -l) )); then
    print_status "OK" "Frontend response time: ${FRONTEND_TIME}s"
else
    print_status "WARNING" "Frontend response time: ${FRONTEND_TIME}s (slow)"
fi

echo ""

# Summary
echo "📊 Health Check Summary:"
echo "========================"

# Count issues
ERRORS=$(grep -c "❌" /tmp/health_check_output 2>/dev/null || echo "0")
WARNINGS=$(grep -c "⚠️" /tmp/health_check_output 2>/dev/null || echo "0")

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    print_status "OK" "All systems operational"
elif [ "$ERRORS" -eq 0 ]; then
    print_status "WARNING" "$WARNINGS warning(s) detected"
else
    print_status "ERROR" "$ERRORS error(s) and $WARNINGS warning(s) detected"
fi

echo ""
echo "🔧 Quick Commands:"
echo "=================="
echo "View backend logs:  tail -f backend/backend.log"
echo "View frontend logs: tail -f frontend/frontend.log"
echo "Restart servers:    ./start_wagelift.sh"
echo "Stop all servers:   pkill -f 'uvicorn|next'"

# Save output for summary counting
exec > >(tee /tmp/health_check_output)