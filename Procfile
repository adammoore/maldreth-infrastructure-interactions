web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload
release: python -c "from app import db, app; app.app_context().push(); db.create_all()"
