#!/bin/bash
# release.sh - Run database migrations and initialization on Heroku

echo "Running database initialization..."
python init_database.py

echo "Release phase complete!"
