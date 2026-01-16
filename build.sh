#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=========================================="
echo "Starting BHV Build Process"
echo "=========================================="

echo ""
echo "[1/4] Upgrading pip..."
pip install --upgrade pip

echo ""
echo "[2/4] Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "[3/4] Creating uploads directory..."
mkdir -p bhv/static/uploads
echo "✓ Uploads directory ready"

echo ""
echo "[4/4] Initializing database..."
python init_db.py

echo ""
echo "=========================================="
echo "Build Process Complete!"
echo "=========================================="