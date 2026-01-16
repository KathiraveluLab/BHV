#!/usr/bin/env bash
set -o errexit
set -x

echo "=== BHV Build Process Started ==="

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Creating uploads directory..."
mkdir -p bhv/static/uploads

echo "Initializing database..."
python init_db.py

echo "=== BHV Build Process Complete ==="