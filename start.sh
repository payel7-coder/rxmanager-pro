#!/bin/bash
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║           RxManager Pro — Prescription System       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

cd /home/claude/rx-manager/backend

# Start Django
echo "▶ Starting Django API server on port 8000..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!
echo "  ✅ Django PID: $DJANGO_PID"

# Start frontend server
cd /home/claude/rx-manager/frontend
echo "▶ Starting Frontend server on port 5500..."
python3 -m http.server 5500 &
FRONT_PID=$!
echo "  ✅ Frontend PID: $FRONT_PID"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  🌐 Frontend:  http://localhost:5500                ║"
echo "║  🔌 API:       http://localhost:8000/api            ║"
echo "║  🛠  Admin:    http://localhost:8000/admin          ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop all servers"

trap "kill $DJANGO_PID $FRONT_PID 2>/dev/null; echo 'Servers stopped.'" EXIT
wait
