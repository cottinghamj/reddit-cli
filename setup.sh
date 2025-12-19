#!/bin/bash

# Reddit CLI Setup Script
# This script sets up the environment for the Reddit CLI application

echo "Setting up Reddit CLI Environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 to continue."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "  source venv/bin/activate"
echo "  python -m src.main \"your search query\""
echo ""
echo "Or in interactive mode:"
echo "  source venv/bin/activate"
echo "  python -m src.main"
