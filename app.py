# Fixed Flask Application (app.py)

```python
import logging
from typing import Dict, List, Union
from flask import Flask, render_template, jsonify, request
from database import query_db, insert_db, init_db, populate_db
from config import DATABASE_CONFIG, APP_CONFIG, LOGGING_CONFIG
import logging.config
import os

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(DATABASE_CONFIG)

# Initialize database on startup instead of using deprecated before_first_request
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

def main():
    try:
        # Initialize the app and database before starting
        initialize_app()
        
        # Get port from environment variable (for Heroku) or use default
        port = int(os.environ.get('PORT', APP_CONFIG['PORT']))
        
        # In production (Heroku), we don't run app.run()
        # The web server (gunicorn) will handle it
        if __name__ == '__main__':
            app.run(host=APP_CONFIG['HOST'], port=port, debug=APP_CONFIG['DEBUG'])
    except Exception as e:
        logger.critical(f"Failed to start the application: {e}")
        raise

# For Heroku, we need the app to be available at module level
# Initialize the database when the module is imported
if __name__ != '__main__':
    initialize_app()

if __name__ == '__main__':
    main()
