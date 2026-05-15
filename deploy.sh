#!/bin/bash
# Run this script from a PythonAnywhere Bash console after cloning the repo.
# Usage: cd ~/freshfield-stock-backend && bash deploy.sh

set -e

PYTHON=python3.13   # adjust if PythonAnywhere offers a newer version
VENV_NAME=freshfield
PROJECT_DIR=~/freshfield-stock-backend

echo "=== 1. Creating virtualenv ==="
mkvirtualenv --python=$PYTHON $VENV_NAME

echo "=== 2. Installing dependencies ==="
cd $PROJECT_DIR
pip install -r requirements.txt

echo "=== 3. Running migrations ==="
python manage.py migrate --noinput

echo "=== 4. Collecting static files ==="
python manage.py collectstatic --noinput

echo ""
echo "=== Done! Now:"
echo "  1. Create your .env file (see .env.example)"
echo "  2. Configure the Web app in the PythonAnywhere dashboard"
echo "  3. Paste the WSGI file content from pythonanywhere_wsgi.py"
