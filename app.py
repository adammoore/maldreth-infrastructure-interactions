import logging
import logging.config
import sqlite3
import json
import os
from typing import Dict, List, Union, Optional, Tuple, Any
from contextlib import closing
from flask import Flask, render_template, jsonify, request

# Configuration
DATABASE_CONFIG = {
    'DATABASE': 'database.db',
    'SQLITE_URI': 'sqlite:///database.db',
    'DEBUG': True,
    'SECRET_KEY': 'your_secret_key_here'
}

APP_CONFIG = {
    'HOST': '0.0.0.0',  # Changed to 0.0.0.0 for Heroku
    'PORT': 5000,
    'DEBUG': False  # Set to False for production
}

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(DATABASE_CONFIG)

# Database functions
def get_db_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DATABASE_CONFIG['DATABASE'])

def init_db() -> None:
    """Initialize the database using the schema."""
    try:
        with closing(get_db_connection()) as db:
            db.cursor().executescript('''
                DROP TABLE IF EXISTS stages;
                DROP TABLE IF EXISTS tool_categories;
                DROP TABLE IF EXISTS tools;
                DROP TABLE IF EXISTS connections;

                CREATE TABLE stages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    x INTEGER,
                    y INTEGER
                );

                CREATE TABLE tool_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stage_id INTEGER,
                    category TEXT NOT NULL,
                    FOREIGN KEY(stage_id) REFERENCES stages(id)
                );

                CREATE TABLE tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    name TEXT NOT NULL,
                    FOREIGN KEY(category_id) REFERENCES tool_categories(id)
                );

                CREATE TABLE connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    view_mode TEXT NOT NULL,
                    from_stage TEXT NOT NULL,
                    to_stage TEXT NOT NULL,
                    type TEXT NOT NULL
                );
            ''')
            db.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        raise

def query_db(query: str, args: Tuple = (), one: bool = False) -> Optional[List[Tuple]]:
    """Execute a database query and return the results."""
    try:
        with closing(get_db_connection()) as db:
            cur = db.execute(query, args)
            rv = cur.fetchall()
            return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        logger.error(f"Error executing query: {e}")
        return None

def insert_db(query: str, args: Tuple = ()) -> int:
    """Execute an insert query and return the last row id."""
    try:
        with closing(get_db_connection()) as db:
            cur = db.cursor()
            cur.execute(query, args)
            db.commit()
            return cur.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error executing insert: {e}")
        raise

def populate_db() -> None:
    """Populate the database with initial data."""
    try:
        with closing(get_db_connection()) as db:
            cursor = db.cursor()

            # Define stages with their positions
            stages_data = [
                ('Conceptualise', 600, 100),
                ('Plan', 800, 200),
                ('Fund', 900, 400),
                ('Collect', 900, 600),
                ('Process', 800, 800),
                ('Analyse', 600, 900),
                ('Store', 400, 900),
                ('Publish', 200, 800),
                ('Preserve', 100, 600),
                ('Share', 100, 400),
                ('Access', 200, 200),
                ('Transform', 400, 100)
            ]

            # Insert stages
            for name, x, y in stages_data:
                cursor.execute('INSERT INTO stages (name, x, y) VALUES (?, ?, ?)', (name, x, y))
                logger.info(f"Inserted stage: {name}")

            # Define connections
            connections_data = [
                ('circular', 'Conceptualise', 'Plan', 'solid'),
                ('circular', 'Plan', 'Fund', 'solid'),
                ('circular', 'Fund', 'Collect', 'solid'),
                ('circular', 'Collect', 'Process', 'solid'),
                ('circular', 'Process', 'Analyse', 'solid'),
                ('circular', 'Analyse', 'Store', 'solid'),
                ('circular', 'Store', 'Publish', 'solid'),
                ('circular', 'Publish', 'Preserve', 'solid'),
                ('circular', 'Preserve', 'Share', 'solid'),
                ('circular', 'Share', 'Access', 'solid'),
                ('circular', 'Access', 'Transform', 'solid'),
                ('circular', 'Transform', 'Conceptualise', 'solid')
            ]

            # Insert connections
            for view_mode, from_stage, to_stage, conn_type in connections_data:
                cursor.execute('INSERT INTO connections (view_mode, from_stage, to_stage, type) VALUES (?, ?, ?, ?)', 
                               (view_mode, from_stage, to_stage, conn_type))
                logger.info(f"Inserted connection from {from_stage} to {to_stage}")

            # Insert tool categories and tools for each stage
            tool_data = {
                'Conceptualise': [
                    ('Mind mapping, concept mapping and knowledge modelling', ['Miro', 'MindMeister', 'XMind']),
                    ('Diagramming and flowchart', ['Lucidchart', 'Draw.io', 'Creately']),
                    ('Wireframing and prototyping', ['Balsamiq', 'Figma'])
                ],
                'Plan': [
                    ('Data management planning (DMP)', ['DMP Tool', 'DMP Online', 'RDMO']),
                    ('Project planning', ['Trello', 'Asana', 'Microsoft Project']),
                    ('Combined DMP/project', ['Data Stewardship Wizard', 'Redbox research data', 'Argos'])
                ],
                'Collect': [
                    ('Quantitative data collection tool', ['Open Data Kit', 'GBIF', 'Cedar WorkBench']),
                    ('Qualitative data collection', ['Survey Monkey', 'Online Surveys', 'Zooniverse']),
                    ('Harvesting tool', ['Netlytic', 'IRODS', 'DROID'])
                ]
            }

            # Get stage IDs
            cursor.execute('SELECT id, name FROM stages')
            stage_map = {name: id for id, name in cursor.fetchall()}

            # Insert tool categories and tools
            for stage_name, categories in tool_data.items():
                if stage_name in stage_map:
                    stage_id = stage_map[stage_name]
                    for category_name, tools in categories:
                        cursor.execute('INSERT INTO tool_categories (stage_id, category) VALUES (?, ?)', 
                                       (stage_id, category_name))
                        category_id = cursor.lastrowid
                        logger.info(f"Inserted category: {category_name} for stage: {stage_name}")
                        
                        for tool in tools:
                            cursor.execute('INSERT INTO tools (category_id, name) VALUES (?, ?)', 
                                           (category_id, tool))
                            logger.info(f"Inserted tool: {tool} for category: {category_name}")

            db.commit()
        logger.info("Database populated successfully.")
    except (sqlite3.Error, json.JSONDecodeError, IOError) as e:
        logger.error(f"Error populating database: {e}")
        raise

# Initialize database on startup
def initialize_app():
    """Initialize the application and database."""
    try:
        init_db()
        # Check if database is empty and populate if needed
        stages = query_db('SELECT COUNT(*) FROM stages')
        if stages and stages[0][0] == 0:
            logger.info("Database is empty, populating with initial data...")
            populate_db()
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise

# Routes
@app.route('/')
def index() -> str:
    """Render the index page."""
    return render_template('index.html')

@app.route('/api/layout/<view_mode>', methods=['GET'])
def get_layout(view_mode: str) -> Union[Dict, tuple]:
    """
    Get the layout for a specific view mode.
    
    Args:
        view_mode (str): The view mode to retrieve the layout for.
    
    Returns:
        Union[Dict, tuple]: The layout data or an error response.
    """
    try:
        stages = query_db('SELECT * FROM stages')
        connections = query_db('SELECT * FROM connections WHERE view_mode = ?', [view_mode])
        
        if not stages:
            logger.warning(f"No stages found for view mode: {view_mode}")
            return jsonify({'error': 'No stages found. Database may need initialization.'}), 404
        
        if not connections:
            logger.warning(f"No connections found for view mode: {view_mode}")
            # Return stages without connections rather than error
            layout = {
                'stages': [{'id': stage[0], 'name': stage[1], 'x': stage[2], 'y': stage[3]} for stage in stages],
                'connections': []
            }
            return jsonify(layout)
        
        layout = {
            'stages': [{'id': stage[0], 'name': stage[1], 'x': stage[2], 'y': stage[3]} for stage in stages],
            'connections': [{'from': conn[2], 'to': conn[3], 'type': conn[4]} for conn in connections]
        }
        return jsonify(layout)
    except Exception as e:
        logger.error(f"Error occurred while getting layout: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

@app.route('/api/stage/<int:stage_id>/categories', methods=['GET'])
def get_categories(stage_id: int) -> Union[List[Dict], tuple]:
    """
    Get categories for a specific stage.
    
    Args:
        stage_id (int): The ID of the stage.
    
    Returns:
        Union[List[Dict], tuple]: A list of categories for the given stage or an error response.
    """
    try:
        categories = query_db('SELECT * FROM tool_categories WHERE stage_id = ?', [stage_id])
        if not categories:
            logger.warning(f"No categories found for stage_id: {stage_id}")
            return jsonify({'error': 'No categories found for the specified stage.'}), 404
        result = [{'id': category[0], 'category': category[2]} for category in categories]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error occurred while getting categories: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

@app.route('/api/category/<int:category_id>/tools', methods=['GET'])
def get_tools(category_id: int) -> Union[List[Dict], tuple]:
    """
    Get tools for a specific category.
    
    Args:
        category_id (int): The ID of the category.
    
    Returns:
        Union[List[Dict], tuple]: A list of tools for the given category or an error response.
    """
    try:
        tools = query_db('SELECT * FROM tools WHERE category_id = ?', [category_id])
        if not tools:
            logger.warning(f"No tools found for category_id: {category_id}")
            return jsonify({'error': 'No tools found for the specified category.'}), 404
        result = [{'id': tool[0], 'name': tool[2]} for tool in tools]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error occurred while getting tools: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

@app.route('/api/category', methods=['POST'])
def add_category() -> Dict:
    """
    Add a new category.
    
    Returns:
        Dict: A status message indicating success or failure.
    """
    data = request.json
    if not data or 'stage_id' not in data or 'category' not in data:
        return jsonify({'error': 'Invalid input data'}), 400
    try:
        insert_db('INSERT INTO tool_categories (stage_id, category) VALUES (?, ?)', [data['stage_id'], data['category']])
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error occurred while adding category: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

@app.route('/api/tool', methods=['POST'])
def add_tool() -> Dict:
    """
    Add a new tool.
    
    Returns:
        Dict: A status message indicating success or failure.
    """
    data = request.json
    if not data or 'category_id' not in data or 'name' not in data:
        return jsonify({'error': 'Invalid input data'}), 400
    try:
        insert_db('INSERT INTO tools (category_id, name) VALUES (?, ?)', [data['category_id'], data['name']])
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error occurred while adding tool: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

@app.route('/api/tool/<int:tool_id>', methods=['DELETE'])
def delete_tool(tool_id: int) -> Dict:
    """
    Delete a tool.
    
    Args:
        tool_id (int): The ID of the tool to delete.
    
    Returns:
        Dict: A status message indicating success or failure.
    """
    try:
        insert_db('DELETE FROM tools WHERE id = ?', [tool_id])
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error occurred while deleting tool: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

@app.route('/api/initialize', methods=['POST'])
def initialize_database():
    """
    Initialize and populate the database.
    
    Returns:
        Dict: A status message indicating success or failure.
    """
    try:
        init_db()
        populate_db()
        return jsonify({'status': 'success', 'message': 'Database initialized and populated successfully'})
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return jsonify({'error': 'Failed to initialize database'}), 500

# Initialize the app when module is imported
try:
    initialize_app()
except Exception as e:
    logger.error(f"Failed to initialize app on import: {e}")
    # Don't raise here to allow the app to start even if initialization fails

if __name__ == '__main__':
    port = int(os.environ.get('PORT', APP_CONFIG['PORT']))
    app.run(host=APP_CONFIG['HOST'], port=port, debug=APP_CONFIG['DEBUG'])
