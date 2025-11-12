#!/bin/bash

# Start Streamlit App for Operation MOS Resume Builder

echo "🎖️ Starting Operation MOS Resume Builder..."

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

# Install/update dependencies
echo "📦 Installing dependencies..."
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

# Start Streamlit
echo ""
echo "✅ Starting Streamlit on http://localhost:8501"
echo "📱 The app will open in your browser automatically"
echo ""
echo "Press Ctrl+C to stop the app"
echo ""

streamlit run app.py
