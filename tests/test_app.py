    """
Test suite for the MaLDReTH Infrastructure Interactions application.

This module contains comprehensive tests for all application functionality
including models, routes, API endpoints, and form submissions.
"""

import pytest
import json
import tempfile
import os
from app import create_app, db
from models import Interaction

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create test app
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for the Flask application's CLI commands."""
    return app.test_cli_runner()

@pytest.fixture
def sample_interaction():
    """Create a sample interaction for testing."""
    return {
        'interaction_type': 'data_flow',
        'source_infrastructure': 'Research Repository',
        'target_infrastructure': 'Analysis Platform',
        'lifecycle_stage': 'analyse',
        'description': 'Automated data transfer from repository to analysis platform',
        'technical_details': 'REST API with OAuth 2.0 authentication',
        'benefits': 'Seamless integration and automated workflow',
        'challenges': 'Network latency and authentication complexity',
        'examples': 'DSpace to R Server integration',
        'contact_person': 'Dr. Jane Smith',
        'organization': 'University XYZ',
        'email': 'jane.smith@university.edu',
        'priority': 'high',
        'complexity': 'moderate',
        'status': 'implemented'
    }

class TestModels:
    """Test cases for database models."""
    
    def test_interaction_creation(self, app, sample_interaction):
        """Test creating a new interaction."""
        with app.app_context():
            interaction = Interaction(**sample_interaction)
            db.session.add(interaction)
            db.session.commit()
            
            assert interaction.id is not None
            assert interaction.interaction_type == 'data_flow'
            assert interaction.source_infrastructure == 'Research Repository'
            assert interaction.created_at is not None
    
    def test_interaction_to_dict(self, app, sample_interaction):
        """Test interaction to_dict method."""
        with app.app_context():
            interaction = Interaction(**sample_interaction)
            db.session.add(interaction)
            db.session.commit()
            
            data = interaction.to_dict()
            assert data['interaction_type'] == 'data_flow'
            assert data['source_infrastructure'] == 'Research Repository'
            assert 'created_at' in data
    
    def test_interaction_validation_methods(self, app):
        """Test interaction class methods for validation."""
        with app.app_context():
            types = Interaction.get_interaction_types()
            assert 'data_flow' in types
            assert 'api_call' in types
            
            stages = Interaction.get_lifecycle_stages()
            assert 'analyse' in stages
            assert 'conceptualise' in stages
            
            priorities = Interaction.get_priority_levels()
            assert 'high' in priorities
            assert 'medium' in priorities
            assert 'low' in priorities

class TestRoutes:
    """Test cases for application routes."""
    
    def test_index_page(self, client):
        """Test the main index page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Infrastructure Interactions' in response.data
    
    def test_add_interaction_page(self, client):
        """Test the add interaction form page."""
        response = client.get('/add')
        assert response.status_code == 200
        assert b'Add New Interaction' in response.data
        assert b'interaction_type' in response.data
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'database' in data
        assert 'interactions_count' in data
    
    def test_view_interactions_empty(self, client):
        """Test viewing interactions when database is empty."""
        response = client.get('/interactions')
        assert response.status_code == 200

class TestAPI:
    """Test cases for API endpoints."""
    
    def test_api_get_interactions_empty(self, client):
        """Test API endpoint with no interactions."""
        response = client.get('/api/interactions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_api_create_interaction(self, client, sample_interaction):
        """Test creating interaction via API."""
        response = client.post('/api/interactions',
                             json=sample_interaction,
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['interaction_type'] == 'data_flow'
        assert data['source_infrastructure'] == 'Research Repository'
        assert 'id' in data
    
    def test_api_create_interaction_missing_fields(self, client):
        """Test API validation with missing required fields."""
        incomplete_data = {
            'interaction_type': 'data_flow',
            'source_infrastructure': 'Test Source'
            # Missing required fields
        }
        
        response = client.post('/api/interactions',
                             json=incomplete_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_get_specific_interaction(self, client, sample_interaction):
        """Test getting a specific interaction via API."""
        # First create an interaction
        response = client.post('/api/interactions',
                             json=sample_interaction,
                             content_type='application/json')
        
        created_data = json.loads(response.data)
        interaction_id = created_data['id']
        
        # Then retrieve it
        response = client.get(f'/api/interactions/{interaction_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['id'] == interaction_id
        assert data['interaction_type'] == 'data_flow'
    
    def test_api_get_nonexistent_interaction(self, client):
        """Test getting a non-existent interaction."""
        response = client.get('/api/interactions/999')
        assert response.status_code == 404

class TestForms:
    """Test cases for form submissions."""
    
    def test_submit_interaction_form(self, client, sample_interaction):
        """Test submitting interaction via form."""
        response = client.post('/submit', data=sample_interaction)
        
        # Should redirect to interactions page
        assert response.status_code == 302
        assert '/interactions' in response.location
    
    def test_submit_interaction_form_missing_fields(self, client):
        """Test form validation with missing required fields."""
        incomplete_data = {
            'interaction_type': 'data_flow',
            'source_infrastructure': 'Test Source'
            # Missing required fields
        }
        
        response = client.post('/submit', data=incomplete_data)
        
        # Should return to form with error
        assert response.status_code == 200
        assert b'Missing required field' in response.data

class TestExport:
    """Test cases for data export functionality."""
    
    def test_export_csv_empty(self, client):
        """Test CSV export with no data."""
        response = client.get('/export')
        assert response.status_code == 200
        assert response.content_type == 'text/csv; charset=utf-8'
        
        # Should contain header row
        assert b'ID,Interaction Type' in response.data
    
    def test_export_csv_with_data(self, client, sample_interaction):
        """Test CSV export with data."""
        # First create an interaction
        client.post('/api/interactions',
                   json=sample_interaction,
                   content_type='application/json')
        
        # Then export
        response = client.get('/export')
        assert response.status_code == 200
        assert response.content_type == 'text/csv; charset=utf-8'
        
        # Should contain header and data
        assert b'ID,Interaction Type' in response.data
        assert b'data_flow' in response.data
        assert b'Research Repository' in response.data

class TestIntegration:
    """Integration test cases."""
    
    def test_full_workflow(self, client, sample_interaction):
        """Test complete workflow from creation to export."""
        # 1. Check initial state
        response = client.get('/')
        assert b'0' in response.data  # Should show 0 interactions
        
        # 2. Create interaction via API
        response = client.post('/api/interactions',
                             json=sample_interaction,
                             content_type='application/json')
        assert response.status_code == 201
        
        # 3. Check it appears on index page
        response = client.get('/')
        assert b'1' in response.data  # Should show 1 interaction
        
        # 4. Check it appears in interactions list
        response = client.get('/interactions')
        assert response.status_code == 200
        assert b'Research Repository' in response.data
        
        # 5. Export to CSV
        response = client.get('/export')
        assert response.status_code == 200
        assert b'Research Repository' in response.data
    
    def test_database_persistence(self, app, sample_interaction):
        """Test that data persists across requests."""
        with app.test_client() as client:
            # Create interaction
            response = client.post('/api/interactions',
                                 json=sample_interaction,
                                 content_type='application/json')
            assert response.status_code == 201
            
            # Verify it exists
            response = client.get('/api/interactions')
            data = json.loads(response.data)
            assert len(data) == 1
            
            # Create another client and verify data still exists
            with app.test_client() as client2:
                response = client2.get('/api/interactions')
                data = json.loads(response.data)
                assert len(data) == 1

class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_invalid_json_api(self, client):
        """Test API with invalid JSON."""
        response = client.post('/api/interactions',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400

if __name__ == '__main__':
    pytest.main(['-v', __file__])
