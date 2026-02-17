#!/bin/bash

# Book Finder API - Setup Script for macOS

echo "🚀 Book Finder API Setup"
echo "========================"
echo ""

# Check if Xcode Command Line Tools are installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Installing Xcode Command Line Tools..."
    echo "Please click 'Install' in the popup dialog."
    xcode-select --install
    echo ""
    echo "⏳ Waiting for installation to complete..."
    echo "After installation completes, run this script again."
    exit 1
else
    echo "✅ Git is installed"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
else
    echo "✅ Python 3 is installed ($(python3 --version))"
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Test locally: python app.py"
echo "2. Visit: http://localhost:5000"
echo "3. Follow DEPLOYMENT_GUIDE.md to deploy to Railway"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
