"""
Research Data Lifecycle Visualization Flask Application
Author: Adam Vials Moore
Date: 20 June 2025

This module sets up the Flask application for serving the research data lifecycle stages,
connections, substages, and tools from a SQLite database.

The application can be run locally or deployed on cloud platforms like Heroku or AWS EC2.
"""

import os
import sqlite3
import logging
from flask import Flask, jsonify, send_from_directory, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    """
    Application factory pattern for creating Flask app instances.
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # Configuration
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
    else:
        # Use environment variable for database URL (Heroku/AWS) or default to local SQLite
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            # Fix for Heroku Postgres URL format
            database_url = database_url.replace('postgres://', 'postgresql://')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///lifecycle.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

def query_db(query: str, args: tuple = (), one: bool = False) -> list:
    """
    Execute a query on the database and return the results.

    Args:
        query (str): SQL query string to execute.
        args (tuple): Arguments for the SQL query. Defaults to an empty tuple.
        one (bool): If True, fetch one result; if False, fetch all. Defaults to False.

    Returns:
        list: Query results as a list of tuples.

    Raises:
        sqlite3.Error: If there's an issue with the database connection or query execution.
    """
    try:
        # Use SQLAlchemy's database connection
        from flask import current_app
        engine = current_app.extensions['sqlalchemy'].db.engine
        with engine.connect() as conn:
            result = conn.execute(query, args)
            rv = result.fetchall()
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise

# Create the application instance
app = create_app()

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database with tables and sample data."""
    with app.app_context():
        db.create_all()
        populate_initial_data()
        logger.info('Database initialized successfully.')

def populate_initial_data():
    """Populate the database with initial research lifecycle data."""
    from models import LifecycleStage, ToolCategory, Tool, LifecycleConnection
    
    # Check if data already exists
    if LifecycleStage.query.first():
        logger.info('Database already contains data. Skipping population.')
        return
    
    # Sample data based on the MaLDReTH model
    stages_data = [
        {'name': 'Conceptualise', 'description': 'To formulate the initial research idea or hypothesis', 'order': 1},
        {'name': 'Plan', 'description': 'To establish a structured strategic framework', 'order': 2},
        {'name': 'Collect', 'description': 'To acquire and store reliable data', 'order': 3},
        {'name': 'Process', 'description': 'To make data analysis-ready', 'order': 4},
        {'name': 'Analyse', 'description': 'To derive insights from processed data', 'order': 5},
        {'name': 'Store', 'description': 'To record data using appropriate technology', 'order': 6},
        {'name': 'Publish', 'description': 'To release research data for others', 'order': 7},
        {'name': 'Preserve', 'description': 'To ensure long-term data accessibility', 'order': 8},
        {'name': 'Share', 'description': 'To make data available to humans and machines', 'order': 9},
        {'name': 'Access', 'description': 'To control and manage data access', 'order': 10},
        {'name': 'Transform', 'description': 'To create new data from original', 'order': 11},
    ]
    
    stages = {}
    for stage_data in stages_data:
        stage = LifecycleStage(**stage_data)
        db.session.add(stage)
        stages[stage_data['name']] = stage
    
    db.session.commit()
    logger.info('Initial data populated successfully.')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    if 'WEBSITE_HOSTNAME' in os.environ:  # Running on Azure
        logger.info("Starting application on Azure...")
        app.run(host='0.0.0.0', port=port)
    elif os.environ.get('DYNO'):  # Running on Heroku
        logger.info("Starting application on Heroku...")
        app.run(host='0.0.0.0', port=port)
    else:
        logger.info("Starting application locally...")
        app.run(debug=debug, port=port)
