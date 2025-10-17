#!/bin/bash

# Development start script with all services

echo "🚀 Starting AutoGen Research Application (Development Mode)"
echo "============================================================"

# Check dependencies
echo "📋 Checking dependencies..."

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20+"
    exit 1
fi

# Check Redis
if ! command -v redis-server &> /dev/null; then
    echo "⚠️  Redis not installed. Installing with Homebrew..."
    brew install redis
fi

# Check if Redis is running
if ! redis-cli ping &> /dev/null; then
    echo "🔄 Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

echo "✓ All dependencies available"
echo ""

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "   Please edit .env if needed"
fi

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Run: uv sync"
    exit 1
fi

# Start services
echo ""
echo "🚀 Starting services..."
echo ""

# Start Flask backend
echo "📡 Starting Flask backend on port 5001..."
python app.py > logs/backend.log 2>&1 &
FLASK_PID=$!
echo "   PID: $FLASK_PID"
sleep 3

# Start Celery worker
echo "🔄 Starting Celery worker..."
celery -A src.autogen_research.tasks.celery_app worker --loglevel=info > logs/celery.log 2>&1 &
CELERY_PID=$!
echo "   PID: $CELERY_PID"
sleep 3

# Start React frontend
echo "⚛️  Starting React frontend on port 3000..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   PID: $FRONTEND_PID"
sleep 3

echo ""
echo "============================================================"
echo "✅ All services started successfully!"
echo "============================================================"
echo ""
echo "🔗 URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:5001"
echo "   API Docs:  http://localhost:5001/api/docs"
echo "   Health:    http://localhost:5001/api/health"
echo ""
echo "📊 Service PIDs:"
echo "   Backend: $FLASK_PID"
echo "   Celery:  $CELERY_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Celery:   tail -f logs/celery.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 To stop all services, press Ctrl+C"
echo ""

# Save PIDs to file
echo "$FLASK_PID $CELERY_PID $FRONTEND_PID" > .pids

# Trap Ctrl+C to cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."

    # Read PIDs from file
    if [ -f .pids ]; then
        read FLASK_PID CELERY_PID FRONTEND_PID < .pids
        kill $FLASK_PID 2>/dev/null && echo "   ✓ Backend stopped"
        kill $CELERY_PID 2>/dev/null && echo "   ✓ Celery stopped"
        kill $FRONTEND_PID 2>/dev/null && echo "   ✓ Frontend stopped"
        rm .pids
    fi

    echo "✅ All services stopped"
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait
