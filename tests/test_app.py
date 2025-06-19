"""
Simple tests for the Flask application.
"""

import pytest
import tempfile
import os
from app import app, init_db, populate_db


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
            populate_db()
        yield client
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


def test_index_page(client):
    """Test that the index page loads."""
    response = client.get('/')
    assert response.status_code == 200


def test_api_layout(client):
    """Test the layout API endpoint."""
    response = client.get('/api/layout/circular')
    assert response.status_code == 200
    data = response.get_json()
    assert 'stages' in data
    assert 'connections' in data
    assert len(data['stages']) > 0


def test_api_categories(client):
    """Test getting categories for a stage."""
    # First, get a stage ID
    response = client.get('/api/layout/circular')
    data = response.get_json()
    if data['stages']:
        stage_id = data['stages'][0]['id']
        response = client.get(f'/api/stage/{stage_id}/categories')
        # It's okay if there are no categories, just check the response
        assert response.status_code in [200, 404]


def test_add_category(client):
    """Test adding a new category."""
    response = client.post('/api/category', 
                          json={'stage_id': 1, 'category': 'Test Category'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'


def test_add_tool(client):
    """Test adding a new tool."""
    # First add a category
    client.post('/api/category', 
                json={'stage_id': 1, 'category': 'Test Category'})
    
    # Then add a tool
    response = client.post('/api/tool', 
                          json={'category_id': 1, 'name': 'Test Tool'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'


if __name__ == '__main__':
    pytest.main([__file__])
