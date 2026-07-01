#!/bin/bash
# RxManager Pro — starts the Django backend on :8000
# Frontend is a static file, just open frontend/index.html in a browser
# (or run: cd frontend && python -m http.server 5500)

set -e
cd "$(dirname "$0")/backend"

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f "db.sqlite3" ]; then
  echo "No database found — running migrations and seeding demo data..."
  python manage.py migrate
  python seed_data.py
fi

echo ""
echo "Starting Django backend on http://localhost:8000"
echo "Open frontend/index.html in your browser to use the app."
echo ""
echo "Demo logins:"
echo "  Doctor:    dr.rahman / doctor123"
echo "  Assistant: asst.rahim / assistant123"
echo ""

python manage.py runserver
