"""
extensions.py
Shared Flask extensions to avoid circular imports.

This module contains Flask extensions that need to be imported
by multiple modules in the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions without app instance
db = SQLAlchemy()
migrate = Migrate()
