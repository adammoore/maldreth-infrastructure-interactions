"""
test_app.py

Comprehensive test suite for the MaLDReTH Infrastructure Interactions application.

This module contains tests for API endpoints, database operations, and
application functionality.

Author: MaLDReTH Development Team
Date: 2024
"""

import json

import pytest

from app import create_app, db
from app.models import Connection, Stage, Tool, ToolCategory


class TestConfig:
    """Test configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def sample_data(app):
    """Create sample test data."""
    with app.app_context():
        # Create stages
        conceptualise = Stage(
            name="Conceptualise", description="Formulate the initial research idea"
        )
        plan = Stage(name="Plan", description="Establish a structured framework")
        db.session.add_all([conceptualise, plan])
        db.session.commit()

        # Create categories
        mind_mapping = ToolCategory(
            category="Mind Mapping",
            description="Tools for mind mapping",
            stage_id=conceptualise.id,
        )
        project_planning = ToolCategory(
            category="Project Planning",
            description="Tools for project planning",
            stage_id=plan.id,
        )
        db.session.add_all([mind_mapping, project_planning])
        db.session.commit()

        # Create tools
        miro = Tool(
            name="Miro",
            description="Collaborative whiteboard",
            link="https://miro.com",
            provider="Miro",
            category_id=mind_mapping.id,
            stage_id=conceptualise.id,
        )
        trello = Tool(
            name="Trello",
            description="Project management tool",
            link="https://trello.com",
            provider="Atlassian",
            category_id=project_planning.id,
            stage_id=plan.id,
        )
        db.session.add_all([miro, trello])
        db.session.commit()

        # Create connection
        connection = Connection(
            from_stage_id=conceptualise.id, to_stage_id=plan.id, type="solid"
        )
        db.session.add(connection)
        db.session.commit()

        return {
            "stages": [conceptualise, plan],
            "categories": [mind_mapping, project_planning],
            "tools": [miro, trello],
            "connections": [connection],
        }


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_get_lifecycle(self, client, sample_data):
        """Test getting lifecycle stages."""
        response = client.get("/api/lifecycle")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["nodes"]) == 2
        assert data["nodes"][0]["name"] == "Conceptualise"
        assert data["nodes"][1]["name"] == "Plan"

    def test_get_connections(self, client, sample_data):
        """Test getting connections."""
        response = client.get("/api/connections")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["from"] == "Conceptualise"
        assert data[0]["to"] == "Plan"
        assert data[0]["type"] == "solid"

    def test_get_substages(self, client, sample_data):
        """Test getting substages for a stage."""
        response = client.get("/api/substages/Conceptualise")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["name"] == "Mind Mapping"

    def test_get_substages_not_found(self, client):
        """Test getting substages for non-existent stage."""
        response = client.get("/api/substages/NonExistent")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 0

    def test_get_tools(self, client, sample_data):
        """Test getting tools for a stage."""
        response = client.get("/api/tools/Conceptualise")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["name"] == "Miro"
        assert data[0]["provider"] == "Miro"

    def test_get_tools_empty(self, client):
        """Test getting tools for stage with no tools."""
        response = client.get("/api/tools/NonExistent")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 0

    def test_search_tools(self, client, sample_data):
        """Test searching tools."""
        response = client.get("/api/search?q=miro")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["name"] == "Miro"

    def test_search_tools_no_results(self, client, sample_data):
        """Test searching tools with no results."""
        response = client.get("/api/search?q=nonexistent")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 0

    def test_search_tools_no_query(self, client):
        """Test searching tools without query parameter."""
        response = client.get("/api/search")
        assert response.status_code == 400

    def test_create_tool(self, client, sample_data):
        """Test creating a new tool."""
        tool_data = {
            "name": "New Tool",
            "description": "Test description",
            "link": "https://example.com",
            "provider": "Test Provider",
            "category_id": sample_data["categories"][0].id,
            "stage_id": sample_data["stages"][0].id,
        }

        response = client.post(
            "/api/tools", data=json.dumps(tool_data), content_type="application/json"
        )
        assert response.status_code == 201

        data = json.loads(response.data)
        assert data["name"] == "New Tool"
        assert data["id"] is not None

    def test_create_tool_invalid(self, client):
        """Test creating a tool with invalid data."""
        tool_data = {"description": "Missing required fields"}

        response = client.post(
            "/api/tools", data=json.dumps(tool_data), content_type="application/json"
        )
        assert response.status_code == 400

    def test_update_tool(self, client, sample_data):
        """Test updating a tool."""
        tool_id = sample_data["tools"][0].id
        update_data = {"description": "Updated description"}

        response = client.put(
            f"/api/tools/{tool_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["description"] == "Updated description"

    def test_update_tool_not_found(self, client):
        """Test updating non-existent tool."""
        response = client.put(
            "/api/tools/999",
            data=json.dumps({"description": "Test"}),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_delete_tool(self, client, sample_data):
        """Test deleting a tool."""
        tool_id = sample_data["tools"][0].id

        response = client.delete(f"/api/tools/{tool_id}")
        assert response.status_code == 204

        # Verify tool is deleted
        with client.application.app_context():
            tool = Tool.query.get(tool_id)
            assert tool is None

    def test_delete_tool_not_found(self, client):
        """Test deleting non-existent tool."""
        response = client.delete("/api/tools/999")
        assert response.status_code == 404


class TestViews:
    """Test HTML views."""

    def test_index_page(self, client):
        """Test index page loads."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"MaLDReTH" in response.data

    def test_visualization_page(self, client):
        """Test visualization page loads."""
        response = client.get("/visualization")
        assert response.status_code == 200

    def test_tools_page(self, client):
        """Test tools page loads."""
        response = client.get("/tools")
        assert response.status_code == 200

    def test_about_page(self, client):
        """Test about page loads."""
        response = client.get("/about")
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling."""

    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test 405 error for wrong method."""
        response = client.post("/api/lifecycle")
        assert response.status_code == 405


class TestDatabaseOperations:
    """Test database operations."""

    def test_cascade_delete(self, app, sample_data):
        """Test cascade delete of stage removes related data."""
        with app.app_context():
            stage = sample_data["stages"][0]
            stage_id = stage.id

            # Delete stage
            db.session.delete(stage)
            db.session.commit()

            # Check related data is deleted
            categories = ToolCategory.query.filter_by(stage_id=stage_id).all()
            assert len(categories) == 0

            tools = Tool.query.filter_by(stage_id=stage_id).all()
            assert len(tools) == 0

    def test_unique_constraints(self, app):
        """Test unique constraints."""
        with app.app_context():
            # Create duplicate stages
            stage1 = Stage(name="Test", description="First")
            stage2 = Stage(name="Test", description="Second")

            db.session.add(stage1)
            db.session.commit()

            db.session.add(stage2)
            with pytest.raises(Exception):  # Should raise IntegrityError
                db.session.commit()


if __name__ == "__main__":
    pytest.main([__file__])
