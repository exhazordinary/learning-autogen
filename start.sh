#!/bin/bash

# Start script for AutoGen Research App with ngrok

echo "🚀 Starting AutoGen Research Application"
echo "========================================"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "⚠️  ngrok is not installed. Please install it from https://ngrok.com/"
    echo "   You can install it with: brew install ngrok"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Start Flask backend in background
echo "📡 Starting Flask backend on port 5001..."
python app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

# Start React frontend in background
echo "⚛️  Starting React frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 3

# Start ngrok tunnel to Flask backend
echo "🌐 Starting ngrok tunnel..."
ngrok http 5001 --log=stdout > ngrok.log &
NGROK_PID=$!

# Wait for ngrok to initialize
sleep 3

# Get ngrok public URL
echo ""
echo "========================================"
echo "✅ Application started successfully!"
echo "========================================"
echo ""
echo "🔗 Local URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5001"
echo ""
echo "🌍 Public URLs (via ngrok):"
curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'https://[^"]*' | head -1
echo ""
echo ""
echo "📝 To stop all services, press Ctrl+C"
echo ""

# Trap Ctrl+C to cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $FLASK_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait
