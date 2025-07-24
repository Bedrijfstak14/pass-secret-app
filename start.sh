#!/bin/sh
echo "Initialiseren database..."
python -c "from app import create_app; create_app()"

echo "Starten met Gunicorn..."
exec gunicorn -w 4 -b 0.0.0.0:5000 app:app
