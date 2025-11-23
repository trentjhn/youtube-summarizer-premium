#!/bin/bash

# YouTube Video Summarizer - Development Startup Script
# This script starts both backend and frontend in separate terminal windows

set -e

echo "🚀 YouTube Video Summarizer - Development Startup"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env exists
if [ ! -f "youtube-summarizer/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo ""
    echo "Creating .env from template..."
    cp youtube-summarizer/.env.example youtube-summarizer/.env
    echo -e "${YELLOW}Please edit youtube-summarizer/.env and add your OPENAI_API_KEY${NC}"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" youtube-summarizer/.env; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not configured in .env${NC}"
    echo "Please edit youtube-summarizer/.env and add your API key"
    exit 1
fi

echo -e "${GREEN}✓ Configuration found${NC}"
echo ""

# Start backend
echo -e "${BLUE}Starting Backend...${NC}"
cd youtube-summarizer
source venv/bin/activate
python src/main.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "  Backend URL: http://localhost:5000"
echo ""

# Wait for backend to start
sleep 2

# Start frontend
echo -e "${BLUE}Starting Frontend...${NC}"
cd ../youtube-summarizer-frontend
pnpm dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "  Frontend URL: http://localhost:5173"
echo ""

echo -e "${GREEN}✅ Both services are running!${NC}"
echo ""
echo "📝 Logs:"
echo "  Backend:  http://localhost:5000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

echo ""
echo -e "${YELLOW}Services stopped${NC}"

