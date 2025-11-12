#!/bin/bash
# Quick setup script for MOS Mapping Excel integration

echo "=========================================="
echo "MOS Mapping Excel Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this from the Resume-Builder directory"
    exit 1
fi

echo "📦 Step 1: Installing openpyxl package..."
pip install openpyxl

echo ""
echo "✅ openpyxl installed successfully!"
echo ""

# Check if Excel file exists
if [ -f "data/MOS Mapping.xlsx" ]; then
    echo "✅ MOS Mapping.xlsx found in data/ directory"
else
    echo "⚠️  MOS Mapping.xlsx not found in data/ directory"
    echo "   Please ensure the Excel file is in the data/ folder"
fi

echo ""
echo "📊 Step 2: Inspecting Excel file structure..."
python3 inspect_excel.py

echo ""
echo "🧪 Step 3: Testing MOS mapping service..."
python3 test_mos_mapping.py

echo ""
echo "=========================================="
echo "✨ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review the output above to ensure everything loaded correctly"
echo "2. Run 'streamlit run app.py' to start the application"
echo "3. Test MOS code lookups in the app (Step 1.5)"
echo ""
