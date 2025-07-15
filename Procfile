web: gunicorn wsgi:app
release: python -c "from streamlined_app import app, init_database_with_maldreth_data; app.app_context().push(); init_database_with_maldreth_data()"
