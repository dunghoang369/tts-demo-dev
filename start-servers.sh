#!/bin/bash

# Start both backend and frontend servers for TTS demo

echo "================================================"
echo "Starting TTS Demo with Authentication"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Check if backend dependencies are installed
if [ ! -f "venv/lib/python3.13/site-packages/flask/__init__.py" ] && [ ! -f "venv/lib/python*/site-packages/flask/__init__.py" ]; then
    echo "Installing backend dependencies..."
    source venv/bin/activate
    pip install -r backend/requirements.txt
    deactivate
fi

# Check if frontend dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo ""
echo "Starting servers..."
echo ""

# Start backend server in background
echo "Starting backend server on http://localhost:5000..."
source venv/bin/activate
python backend/server.py &
BACKEND_PID=$!
deactivate

# Wait for backend to start
sleep 2

# Start frontend server
echo "Starting frontend server on http://localhost:5173..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "================================================"
echo "Servers started successfully!"
echo "================================================"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:5000"
echo ""
echo "Demo Credentials:"
echo "  admin / admin123"
echo "  demo  / demo123"
echo "  user  / password"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "================================================"
echo ""

# Wait for user to press Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait



