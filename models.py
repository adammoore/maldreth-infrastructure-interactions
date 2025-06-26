"""
models.py
Database models for the MaLDReTH application.

This module defines all SQLAlchemy models for the application,
including stages, tools, connections, and user interactions.
"""

from datetime import datetime
from extensions import db


class Stage(db.Model):
    """
    Model representing a stage in the research data lifecycle.
    
    Attributes:
        id (int): Primary key
        name (str): Stage name
        description (str): Stage description
        position (int): Order position in the lifecycle
        tool_categories (relationship): Related tool categories
        tools (relationship): Related tools
    """
    __tablename__ = 'stages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, default=0)
    
    # Relationships
    tool_categories = db.relationship(
        'ToolCategory',
        backref='stage',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    tools = db.relationship(
        'Tool',
        backref='stage',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        """String representation of the stage."""
        return f'<Stage {self.name}>'
    
    def to_dict(self):
        """Convert stage to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'position': self.position
        }


class ToolCategory(db.Model):
    """
    Model representing a category of tools within a stage.
    
    Attributes:
        id (int): Primary key
        name (str): Category name
        description (str): Category description
        stage_id (int): Foreign key to stage
        tools (relationship): Related tools
    """
    __tablename__ = 'tool_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage_id = db.Column(
        db.Integer,
        db.ForeignKey('stages.id'),
        nullable=False
    )
    
    # Relationships
    tools = db.relationship(
        'Tool',
        backref='category',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        """String representation of the tool category."""
        return f'<ToolCategory {self.name}>'


class Tool(db.Model):
    """
    Model representing a specific tool.
    
    Attributes:
        id (int): Primary key
        name (str): Tool name
        description (str): Tool description
        url (str): Tool website URL
        category_id (int): Foreign key to tool category
        stage_id (int): Foreign key to stage
    """
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('tool_categories.id'),
        nullable=True
    )
    stage_id = db.Column(
        db.Integer,
        db.ForeignKey('stages.id'),
        nullable=False
    )
    
    def __repr__(self):
        """String representation of the tool."""
        return f'<Tool {self.name}>'
    
    def to_dict(self):
        """Convert tool to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'category': self.category.name if self.category else None,
            'stage': self.stage.name if self.stage else None
        }


class Connection(db.Model):
    """
    Model representing connections between stages.
    
    Attributes:
        id (int): Primary key
        from_stage_id (int): Source stage ID
        to_stage_id (int): Target stage ID
        connection_type (str): Type of connection (solid, dashed)
    """
    __tablename__ = 'connections'
    
    id = db.Column(db.Integer, primary_key=True)
    from_stage_id = db.Column(
        db.Integer,
        db.ForeignKey('stages.id'),
        nullable=False
    )
    to_stage_id = db.Column(
        db.Integer,
        db.ForeignKey('stages.id'),
        nullable=False
    )
    connection_type = db.Column(
        db.String(50),
        default='solid'
    )
    
    # Relationships
    from_stage = db.relationship(
        'Stage',
        foreign_keys=[from_stage_id],
        backref='outgoing_connections'
    )
    to_stage = db.relationship(
        'Stage',
        foreign_keys=[to_stage_id],
        backref='incoming_connections'
    )
    
    def __repr__(self):
        """String representation of the connection."""
        return f'<Connection {self.from_stage_id} -> {self.to_stage_id}>'


class SiteInteraction(db.Model):
    """
    Model for tracking site interactions and analytics.
    
    Attributes:
        id (int): Primary key
        page_viewed (str): Page that was viewed
        timestamp (datetime): When the interaction occurred
        session_id (str): Session identifier
        user_agent (str): User's browser information
    """
    __tablename__ = 'site_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    page_viewed = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))
    user_agent = db.Column(db.String(500))
    
    def __repr__(self):
        """String representation of the site interaction."""
        return f'<SiteInteraction {self.page_viewed} at {self.timestamp}>'


class UserInteraction(db.Model):
    """
    Model for storing user feedback and interactions.
    
    Attributes:
        id (int): Primary key
        name (str): User's name
        email (str): User's email
        organization (str): User's organization
        role (str): User's role
        feedback (str): User's feedback text
        submitted_at (datetime): When feedback was submitted
    """
    __tablename__ = 'user_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(200))
    role = db.Column(db.String(100))
    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        """String representation of the user interaction."""
        return f'<UserInteraction {self.email} at {self.submitted_at}>'
    
    def to_dict(self):
        """Convert user interaction to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'organization': self.organization,
            'role': self.role,
            'feedback': self.feedback,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
