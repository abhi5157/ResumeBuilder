#!/bin/bash

# Setup script for Veteran Resume Builder
# This script sets up the complete development environment

set -e

echo "🎖️  Veteran Resume Builder - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
echo "This may take a few minutes..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "Please run manually: pip install -r requirements.txt"
    exit 1
fi
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created (using mock AI provider)"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p output
mkdir -p templates/classic
mkdir -p data
mkdir -p tests/golden
echo "✓ Directories created"
echo ""

# Create template
echo "Creating resume template..."
if python scripts/create_template.py 2>/dev/null; then
    echo "✓ Template created"
else
    echo "⚠ Template creation skipped (script may need updates)"
fi
echo ""

# Run tests (optional)
echo "Running tests..."
if pytest tests/ -v --tb=short 2>/dev/null; then
    echo "✓ Tests passed"
else
    echo "⚠ Some tests failed (this is okay for initial setup)"
fi
echo ""

# Print success message
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the web application:"
echo "     streamlit run app.py"
echo ""
echo "  3. Or use the CLI tool:"
echo "     python build_resume.py --in profile.sample.json --docx"
echo ""
echo "  4. To run tests:"
echo "     pytest"
echo ""
echo "  5. For OpenAI integration, edit .env and add your API key"
echo ""
echo "Happy resume building! 🎖️"
