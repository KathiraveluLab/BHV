#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
mkdir -p static/uploads
python init_db.py