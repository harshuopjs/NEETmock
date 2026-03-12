#!/bin/bash
# Start both backend and frontend locally

echo "Starting Backend..."
cd backend
source venv/bin/activate
# Run backend in the background
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend..."
cd ../frontend
# Run frontend in the foreground
npm run dev

# When frontend stops (Ctrl+C), kill backend
kill $BACKEND_PID
