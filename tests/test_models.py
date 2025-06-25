"""
test_models.py

Comprehensive test suite for database models.

This module contains tests for all database models, their relationships,
and constraints.

Author: MaLDReTH Development Team
Date: 2024
"""

import pytest
from datetime import datetime
from app import create_app, db
from app.models import Stage, ToolCategory, Tool, Connection


class TestConfig:
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
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


class TestStageModel:
    """Test Stage model."""
    
    def test_create_stage(self, app):
        """Test creating a stage."""
        with app.app_context():
            stage = Stage(
                name="Test Stage",
                description="Test Description"
            )
            db.session.add(stage)
            db.session.commit()
            
            assert stage.id is not None
            assert stage.name == "Test Stage"
            assert stage.description == "Test Description"
            assert stage.created_at is not None
            
    def test_stage_repr(self, app):
        """Test stage string representation."""
        with app.app_context():
            stage = Stage(name="Test Stage")
            assert repr(stage) == "<Stage 'Test Stage'>"
            
    def test_stage_relationships(self, app):
        """Test stage relationships."""
        with app.app_context():
            stage = Stage(name="Test Stage")
            db.session.add(stage)
            db.session.commit()
            
            # Add category
            category = ToolCategory(
                category="Test Category",
                stage_id=stage.id
            )
            db.session.add(category)
            db.session.commit()
            
            # Test relationship
            assert len(stage.categories) == 1
            assert stage.categories[0].category == "Test Category"
            
    def test_stage_unique_name(self, app):
        """Test stage name uniqueness."""
        with app.app_context():
            stage1 = Stage(name="Unique")
            stage2 = Stage(name="Unique")
            
            db.session.add(stage1)
            db.session.commit()
            
            db.session.add(stage2)
            with pytest.raises(Exception):
                db.session.commit()


class TestToolCategoryModel:
    """Test ToolCategory model."""
    
    def test_create_category(self, app):
        """Test creating a tool category."""
        with app.app_context():
            stage = Stage(name="Test Stage")
            db.session.add(stage)
            db.session.commit()
            
            category = ToolCategory(
                category="Test Category",
                description="Test Description",
                stage_id=stage.id
            )
            db.session.add(category)
            db.session.commit()
            
            assert category.id is not None
            assert category.category == "Test Category"
            assert category.stage.name == "Test Stage"
            
    def test_category_repr(self, app):
        """Test category string representation."""
        with app.app_context():
            category = ToolCategory(category="Test Category")
            assert repr(category) == "<ToolCategory 'Test Category'>"
            
    def test_category_tools_relationship(self, app):
        """Test category-tools relationship."""
        with app.app_context():
            stage = Stage(name="Test Stage")
            db.session.add(stage)
            db.session.commit()
            
            category = ToolCategory(
                category="Test Category",
                stage_id=stage.id
            )
            db.session.add(category)
            db.session.commit()
            
            # Add tools
            tool1 = Tool(
                name="Tool 1",
                category_id=category.id,
                stage_id=stage.id
            )
            tool2 = Tool(
                name="Tool 2",
                category_id=category.id,
                stage_id=stage.id
            )
            db.session.add_all([tool1, tool2])
            db.session.commit()
            
            assert len(category.tools) == 2
            
    def test_category_cascade_delete(self, app):
        """Test cascade delete from stage to category."""
        with app.app_context():
            stage = Stage(name="Test Stage")
            db.session.add(stage)
            db.session.commit()
            
            category = ToolCategory(
                category="Test Category",
                stage_id=stage.id
            )
            db.session.add(category)
            db.session.commit()
            
            category_id = category.id
            
            # Delete stage
            db.session.delete(stage)
            db.session.commit()
            
            # Category should be deleted
            assert ToolCategory.query.get(category_id) is None


class TestToolModel:
    """Test Tool model."""
    
    def test_create_tool(self, app):
        """Test creating a tool."""
        with app.app_context():
            stage = Stage(name="Test Stage")
            db.session.add(stage)
            db.session.commit()
            
            category = ToolCategory(
                category="Test Category",
                stage_id=stage.id
            )
            db.session.add(category)
            db.session.commit()
            
            tool = Tool(
                name="Test Tool",
                description="Test Description",
                link="https://example.com",
                provider="Test Provider",
                category_id=category.id,
                stage_id=stage.id
            )
            db.session.add(tool)
            db.session.commit()
            
            assert tool.id is not None
            assert tool.name == "Test Tool"
            assert tool.stage.name == "Test Stage"
            assert tool.category.category == "Test Category"
            
    def test_tool_repr(self, app):
        """Test tool string representation."""
        with app.app_context():
            tool = Tool(name="Test Tool")
            assert repr(tool) == "<Tool 'Test Tool'>"
            
    def test_tool_optional_fields(self, app):
        """Test tool with optional fields."""
        with app.app_context():
            stage = Stage(name="Test Stage")
            category = ToolCategory(
                category="Test Category",
                stage=stage
            )
            db.session.add_all([stage, category])
            db.session.commit()
            
            # Create tool with only required fields
            tool = Tool(
                name="Minimal Tool",
                category_id=category.id,
                stage_id=stage.id
            )
            db.session.add(tool)
            db.session.commit()
            
            assert tool.description is None
            assert tool.link is None
            assert tool.provider is None
            
    def test_tool_cascade_delete(self, app):
        """Test cascade delete from category to tool."""
        with app.app_context():
            stage = Stage(name="Test Stage")
            category = ToolCategory(
                category="Test Category",
                stage=stage
            )
            db.session.add_all([stage, category])
            db.session.commit()
            
            tool = Tool(
                name="Test Tool",
                category_id=category.id,
                stage_id=stage.id
            )
            db.session.add(tool)
            db.session.commit()
            
            tool_id = tool.id
            
            # Delete category
            db.session.delete(category)
            db.session.commit()
            
            # Tool should be deleted
            assert Tool.query.get(tool_id) is None


class TestConnectionModel:
    """Test Connection model."""
    
    def test_create_connection(self, app):
        """Test creating a connection."""
        with app.app_context():
            stage1 = Stage(name="Stage 1")
            stage2 = Stage(name="Stage 2")
            db.session.add_all([stage1, stage2])
            db.session.commit()
            
            connection = Connection(
                from_stage_id=stage1.id,
                to_stage_id=stage2.id,
                type="solid"
            )
            db.session.add(connection)
            db.session.commit()
            
            assert connection.id is not None
            assert connection.from_stage.name == "Stage 1"
            assert connection.to_stage.name == "Stage 2"
            assert connection.type == "solid"
            
    def test_connection_repr(self, app):
        """Test connection string representation."""
        with app.app_context():
            stage1 = Stage(name="Stage 1")
            stage2 = Stage(name="Stage 2")
            db.session.add_all([stage1, stage2])
            db.session.commit()
            
            connection = Connection(
                from_stage=stage1,
                to_stage=stage2
            )
            assert repr(connection) == "<Connection 'Stage 1' -> 'Stage 2'>"
            
    def test_connection_types(self, app):
        """Test different connection types."""
        with app.app_context():
            stage1 = Stage(name="Stage 1")
            stage2 = Stage(name="Stage 2")
            db.session.add_all([stage1, stage2])
            db.session.commit()
            
            # Solid connection
            solid_conn = Connection(
                from_stage_id=stage1.id,
                to_stage_id=stage2.id,
                type="solid"
            )
            
            # Dashed connection
            dashed_conn = Connection(
                from_stage_id=stage2.id,
                to_stage_id=stage1.id,
                type="dashed"
            )
            
            db.session.add_all([solid_conn, dashed_conn])
            db.session.commit()
            
            assert solid_conn.type == "solid"
            assert dashed_conn.type == "dashed"
            
    def test_connection_self_reference(self, app):
        """Test connection can reference same stage."""
        with app.app_context():
            stage = Stage(name="Stage")
            db.session.add(stage)
            db.session.commit()
            
            connection = Connection(
                from_stage_id=stage.id,
                to_stage_id=stage.id,
                type="solid"
            )
            db.session.add(connection)
            db.session.commit()
            
            assert connection.from_stage_id == connection.to_stage_id
            
    def test_connection_cascade_delete(self, app):
        """Test cascade delete when stage is deleted."""
        with app.app_context():
            stage1 = Stage(name="Stage 1")
            stage2 = Stage(name="Stage 2")
            db.session.add_all([stage1, stage2])
            db.session.commit()
            
            connection = Connection(
                from_stage_id=stage1.id,
                to_stage_id=stage2.id
            )
            db.session.add(connection)
            db.session.commit()
            
            connection_id = connection.id
            
            # Delete stage
            db.session.delete(stage1)
            db.session.commit()
            
            # Connection should be deleted
            assert Connection.query.get(connection_id) is None


class TestModelValidation:
    """Test model validation."""
    
    def test_stage_name_required(self, app):
        """Test stage name is required."""
        with app.app_context():
            stage = Stage(description="No name")
            db.session.add(stage)
            
            with pytest.raises(Exception):
                db.session.commit()
                
    def test_tool_category_required(self, app):
        """Test tool category is required."""
        with app.app_context():
            stage = Stage(name="Test")
            db.session.add(stage)
            db.session.commit()
            
            tool = Tool(
                name="Test Tool",
                stage_id=stage.id
                # Missing category_id
            )
            db.session.add(tool)
            
            with pytest.raises(Exception):
                db.session.commit()
                
    def test_connection_stages_required(self, app):
        """Test connection stages are required."""
        with app.app_context():
            connection = Connection(type="solid")
            # Missing from_stage_id and to_stage_id
            db.session.add(connection)
            
            with pytest.raises(Exception):
                db.session.commit()


class TestComplexQueries:
    """Test complex database queries."""
    
    def test_get_tools_by_stage(self, app):
        """Test getting all tools for a stage."""
        with app.app_context():
            # Create test data
            stage1 = Stage(name="Stage 1")
            stage2 = Stage(name="Stage 2")
            db.session.add_all([stage1, stage2])
            db.session.commit()
            
            cat1 = ToolCategory(category="Cat 1", stage_id=stage1.id)
            cat2 = ToolCategory(category="Cat 2", stage_id=stage2.id)
            db.session.add_all([cat1, cat2])
            db.session.commit()
            
            # Add tools to stage 1
            for i in range(3):
                tool = Tool(
                    name=f"Tool {i}",
                    category_id=cat1.id,
                    stage_id=stage1.id
                )
                db.session.add(tool)
                
            # Add tools to stage 2
            tool = Tool(
                name="Other Tool",
                category_id=cat2.id,
                stage_id=stage2.id
            )
            db.session.add(tool)
            db.session.commit()
            
            # Query tools for stage 1
            stage1_tools = Tool.query.filter_by(stage_id=stage1.id).all()
            assert len(stage1_tools) == 3
            
    def test_get_connected_stages(self, app):
        """Test getting connected stages."""
        with app.app_context():
            # Create circular connection
            stages = []
            for i in range(4):
                stage = Stage(name=f"Stage {i}")
                stages.append(stage)
            db.session.add_all(stages)
            db.session.commit()
            
            # Create connections: 0->1->2->3->0
            for i in range(4):
                connection = Connection(
                    from_stage_id=stages[i].id,
                    to_stage_id=stages[(i + 1) % 4].id
                )
                db.session.add(connection)
            db.session.commit()
            
            # Get connections from Stage 0
            connections = Connection.query.filter_by(
                from_stage_id=stages[0].id
            ).all()
            assert len(connections) == 1
            assert connections[0].to_stage.name == "Stage 1"
            
    def test_search_tools(self, app):
        """Test searching tools by name."""
        with app.app_context():
            stage = Stage(name="Test")
            category = ToolCategory(category="Test", stage=stage)
            db.session.add_all([stage, category])
            db.session.commit()
            
            # Add tools with different names
            tools_data = [
                ("Miro", "Whiteboard tool"),
                ("Trello", "Project management"),
                ("Figma", "Design tool"),
                ("Microsoft Project", "Project management")
            ]
            
            for name, desc in tools_data:
                tool = Tool(
                    name=name,
                    description=desc,
                    category_id=category.id,
                    stage_id=stage.id
                )
                db.session.add(tool)
            db.session.commit()
            
            # Search for "project"
            results = Tool.query.filter(
                db.or_(
                    Tool.name.ilike('%project%'),
                    Tool.description.ilike('%project%')
                )
            ).all()
            
            assert len(results) == 2
            assert all('project' in r.name.lower() or 'project' in r.description.lower() 
                      for r in results)


if __name__ == '__main__':
    pytest.main([__file__])
