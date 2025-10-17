#!/bin/bash

# Status check script

echo "🔍 AutoGen Research Assistant - Status Check"
echo "============================================"
echo ""

# Check Backend
echo "📡 Backend (Flask):"
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "   ✓ Running on http://localhost:5001"
    health=$(curl -s http://localhost:5001/api/health | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    echo "   Status: $health"
else
    echo "   ✗ Not running"
fi
echo ""

# Check Frontend
echo "⚛️  Frontend (React):"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✓ Running on http://localhost:3000"
else
    echo "   ✗ Not running"
fi
echo ""

# Check Redis
echo "💾 Redis:"
if redis-cli ping > /dev/null 2>&1; then
    echo "   ✓ Running"
else
    echo "   ✗ Not running"
fi
echo ""

# Check Celery
echo "🔄 Celery Worker:"
if pgrep -f "celery.*worker" > /dev/null 2>&1; then
    echo "   ✓ Running"
    worker_count=$(pgrep -f "celery.*worker" | wc -l)
    echo "   Workers: $worker_count"
else
    echo "   ✗ Not running"
fi
echo ""

# Check ngrok
echo "🌐 ngrok:"
if pgrep -f "ngrok" > /dev/null 2>&1; then
    echo "   ✓ Running"
    if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
        public_url=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'https://[^"]*' | head -1)
        if [ ! -z "$public_url" ]; then
            echo "   Public URL: $public_url"
        fi
    fi
else
    echo "   ✗ Not running"
fi
echo ""

echo "============================================"
echo ""
echo "Quick commands:"
echo "  Start all:   ./start_dev.sh"
echo "  Basic mode:  ./start.sh"
echo "  Docker:      docker-compose up -d"
echo "  Stop:        Press Ctrl+C or kill processes"
echo ""
