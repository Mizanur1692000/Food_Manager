#!/bin/bash
# Run the Restaurant Inventory App with the correct virtual environment

# Change to script directory
cd "$(dirname "$0")"

# Check if venv_fresh exists
if [ ! -d "venv_fresh" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv_fresh
    echo "Installing dependencies..."
    ./venv_fresh/bin/pip install -r requirements.txt
fi

# Run Streamlit
echo "Starting Restaurant Inventory App..."
./venv_fresh/bin/streamlit run app.py
