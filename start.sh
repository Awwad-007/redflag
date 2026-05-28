#!/bin/bash
# RedFlag — Start both servers

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "🚩 RedFlag — Legal Clarity Engine"
echo "=================================="
echo ""

# Check backend .env
if [ ! -f "$ROOT_DIR/backend/.env" ]; then
  echo "❌  backend/.env not found."
  echo "   Run: cp backend/.env.example backend/.env"
  echo "   Then add your GROQ_API_KEY from https://console.groq.com"
  exit 1
fi

# Check GROQ key is set
GROQ_KEY=$(grep -E '^GROQ_API_KEY=' "$ROOT_DIR/backend/.env" | cut -d= -f2 | tr -d ' ')
if [ -z "$GROQ_KEY" ]; then
  echo "❌  GROQ_API_KEY is empty in backend/.env"
  echo "   Get a free key at https://console.groq.com"
  exit 1
fi

# Check node_modules
if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  echo "⚠️   node_modules not found — running npm install first..."
  cd "$ROOT_DIR/frontend" && npm install --silent && cd "$ROOT_DIR"
fi

cleanup() {
  echo ""
  echo "🛑  Shutting down RedFlag..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Start backend
echo "▶  Starting backend   →  http://localhost:8000"
cd "$ROOT_DIR/backend"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "   Waiting for backend..."
for i in $(seq 1 15); do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   Backend ready ✓"
    break
  fi
  sleep 1
done

# Start frontend
echo "▶  Starting frontend  →  http://localhost:5173"
cd "$ROOT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║  RedFlag is running                   ║"
echo "║                                       ║"
echo "║  Web app:   http://localhost:5173     ║"
echo "║  API docs:  http://localhost:8000/docs ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop."
echo ""

wait
