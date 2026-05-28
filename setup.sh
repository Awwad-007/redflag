#!/bin/bash
# RedFlag — First-time setup script
set -e

echo ""
echo "🚩 RedFlag — Setup"
echo "=================="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌  Python 3 not found. Install it from https://python.org"
  exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
  echo "❌  Node.js not found. Install it from https://nodejs.org"
  exit 1
fi

# Backend deps
echo "📦  Installing backend dependencies..."
cd backend
pip install -r requirements.txt -q
cd ..

# Frontend deps
echo "📦  Installing frontend dependencies..."
cd frontend
npm install --silent
cd ..

echo ""
echo "✅  Setup complete! Run ./start.sh to launch RedFlag."
echo ""
