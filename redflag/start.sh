#!/bin/bash
# RedFlag — Quick Start Script

echo ""
echo "🚩 RedFlag — Legal Clarity Engine"
echo "=================================="
echo ""

# Check for GROQ_API_KEY
if [ ! -f "backend/.env" ]; then
  echo "⚠️  backend/.env not found."
  echo "   Copy backend/.env.example → backend/.env"
  echo "   Add your GROQ_API_KEY from https://console.groq.com"
  echo ""
  exit 1
fi

# Start backend
echo "▶ Starting backend (FastAPI on :8000)..."
cd backend && uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend
echo "▶ Starting frontend (Vite on :5173)..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ RedFlag is running!"
echo "   Frontend: http://localhost:5173"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

# Wait and cleanup
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
