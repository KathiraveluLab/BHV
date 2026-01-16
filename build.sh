#!/usr/bin/env bash
set -o errexit  # Exit on error
set -x          # Print commands (for debugging)

echo "=== BHV Build Process Started ==="

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p bhv/static/uploads

# Initialize database
echo "Initializing database..."
python init_db.py

echo "=== BHV Build Process Complete ==="
