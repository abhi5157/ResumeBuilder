#!/bin/bash

# Start FastAPI Backend for Operation MOS Resume Builder

echo "🚀 Starting Operation MOS Backend..."

# Navigate to project root
cd "$(dirname "$0")"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Please update .env with your OpenAI API key"
    else
        echo "❌ .env.example not found. Please create .env manually"
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update backend dependencies
echo "📦 Installing backend dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check OpenAI configuration
echo "🔍 Checking AI configuration..."
if grep -q "your_openai_api_key_here\|sk-your-openai-api-key-here" .env 2>/dev/null; then
    echo "⚠️  WARNING: Please update OPENAI_API_KEY in .env file"
    echo "   Using mock AI provider for testing"
else
    echo "✓ OpenAI API key configured"
fi

# Start the server
echo ""
echo "✅ Starting server on http://localhost:8000"
echo "📱 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000