#!/bin/bash

echo "🗣️  Starting Talk to Your Data System"
echo "======================================"

# Load environment variables
export $(cat .env | xargs)

# Kill any existing processes on ports 8000 and 5173
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Start backend in background
echo "🚀 Starting backend server..."
cd backend && python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🚀 Starting frontend server..."
cd ../frontend && npm run dev -- --force &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are starting up!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 To test with sample data:"
echo "   Connection string: sqlite:///test_database.db"
echo ""
echo "⏹️  Press Ctrl+C to stop both servers"

# Wait for user to stop
wait

# Cleanup on exit
echo ""
echo "🛑 Stopping servers..."
kill $BACKEND_PID 2>/dev/null || true
kill $FRONTEND_PID 2>/dev/null || true
echo "✅ Servers stopped"
