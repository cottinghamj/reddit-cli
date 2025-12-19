#!/bin/bash

# Run the Reddit CLI application
# This script provides an easy way to run the Reddit CLI application

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
python -m src.main "$@"

# Deactivate virtual environment
deactivate
