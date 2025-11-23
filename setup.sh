#!/bin/bash

# YouTube Video Summarizer - Setup Script
# This script sets up both backend and frontend for development

set -e  # Exit on error

echo "🚀 YouTube Video Summarizer - Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend Setup
echo -e "${BLUE}📦 Setting up Backend...${NC}"
echo ""

cd youtube-summarizer

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✓ Backend dependencies installed${NC}"
echo ""

# Frontend Setup
echo -e "${BLUE}📦 Setting up Frontend...${NC}"
echo ""

cd ../youtube-summarizer-frontend

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies with pnpm...${NC}"
pnpm install

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
echo ""

# Return to root
cd ..

echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Create a .env file in youtube-summarizer/ with:"
echo "   OPENAI_API_KEY=your-api-key-here"
echo "   SECRET_KEY=your-secret-key-here"
echo "   FLASK_ENV=development"
echo ""
echo "2. Start the backend:"
echo "   cd youtube-summarizer"
echo "   source venv/bin/activate"
echo "   python src/main.py"
echo ""
echo "3. In another terminal, start the frontend:"
echo "   cd youtube-summarizer-frontend"
echo "   pnpm dev"
echo ""
echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "📚 For more information, see DEPLOYMENT.md"

