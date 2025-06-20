"""
Database models for the Research Data Lifecycle Visualization application.

This module defines the SQLAlchemy models for representing lifecycle stages,
tool categories, tools, and their relationships in the database.
"""

from datetime import datetime
from app import db

class LifecycleStage(db.Model):
    """
    Model representing a stage in the research data lifecycle.
    
    Attributes:
        id (int): Primary key of the stage
        name (str): Name of the lifecycle stage
        description (str): Description of what this stage involves
        order (int): Order of the stage in the lifecycle
        created_at (datetime): When the stage was created
        tool_categories (relationship): Related ToolCategory objects
        outgoing_connections (relationship): Outgoing connections to other stages
        incoming_connections (relationship): Incoming connections from other stages
    """
    __tablename__ = 'lifecycle_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tool_categories = db.relationship('ToolCategory', backref='stage', lazy='dynamic', cascade='all, delete-orphan')
    outgoing_connections = db.relationship('LifecycleConnection', 
                                         foreign_keys='LifecycleConnection.from_stage_id',
                                         backref='from_stage', lazy='dynamic')
    incoming_connections = db.relationship('LifecycleConnection',
                                         foreign_keys='LifecycleConnection.to_stage_id', 
                                         backref='to_stage', lazy='dynamic')

    def to_dict(self):
        """Convert the stage to a dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tool_categories': [category.to_dict() for category in self.tool_categories]
        }

    def __repr__(self):
        return f"<LifecycleStage(name='{self.name}', order={self.order})>"

class ToolCategory(db.Model):
    """
    Model representing a tool category within a lifecycle stage.
    
    Attributes:
        id (int): Primary key of the category
        name (str): Name of the tool category
        description (str): Description of the category
        stage_id (int): Foreign key to the parent LifecycleStage
        created_at (datetime): When the category was created
        tools (relationship): Related Tool objects
    """
    __tablename__ = 'tool_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tools = db.relationship('Tool', backref='category', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert the category to a dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stage_id': self.stage_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tools': [tool.to_dict() for tool in self.tools]
        }

    def __repr__(self):
        return f"<ToolCategory(name='{self.name}', stage_id={self.stage_id})>"

class Tool(db.Model):
    """
    Model representing a specific tool within a tool category.
    
    Attributes:
        id (int): Primary key of the tool
        name (str): Name of the tool
        description (str): Description of the tool
        url (str): URL link to the tool
        provider (str): Provider or creator of the tool
        tool_type (str): Type classification of the tool
        source (str): Whether the tool is 'open' or 'closed' source
        scope (str): Scope of the tool (e.g., 'Generic', 'Disciplinary')
        is_interoperable (bool): Whether the tool supports interoperability
        category_id (int): Foreign key to the parent ToolCategory
        created_at (datetime): When the tool was created
    """
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    provider = db.Column(db.String(200))
    tool_type = db.Column(db.String(200))
    source = db.Column(db.String(50))  # 'open' or 'closed'
    scope = db.Column(db.String(100))  # 'Generic' or 'Disciplinary'
    is_interoperable = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert the tool to a dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'provider': self.provider,
            'tool_type': self.tool_type,
            'source': self.source,
            'scope': self.scope,
            'is_interoperable': self.is_interoperable,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Tool(name='{self.name}', provider='{self.provider}')>"

class LifecycleConnection(db.Model):
    """
    Model representing connections between lifecycle stages.
    
    Attributes:
        id (int): Primary key of the connection
        from_stage_id (int): Foreign key to the source stage
        to_stage_id (int): Foreign key to the destination stage
        connection_type (str): Type of connection ('normal', 'alternative', 'feedback')
        description (str): Optional description of the connection
        created_at (datetime): When the connection was created
    """
    __tablename__ = 'lifecycle_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    from_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    to_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    connection_type = db.Column(db.String(50), default='normal')  # 'normal', 'alternative', 'feedback'
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a stage cannot connect to itself
    __table_args__ = (
        db.CheckConstraint('from_stage_id != to_stage_id', name='no_self_connection'),
        db.UniqueConstraint('from_stage_id', 'to_stage_id', name='unique_connection'),
    )

    def to_dict(self):
        """Convert the connection to a dictionary representation."""
        return {
            'id': self.id,
            'from_stage_id': self.from_stage_id,
            'to_stage_id': self.to_stage_id,
            'from_stage_name': self.from_stage.name if self.from_stage else None,
            'to_stage_name': self.to_stage.name if self.to_stage else None,
            'connection_type': self.connection_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<LifecycleConnection(from={self.from_stage_id}, to={self.to_stage_id}, type='{self.connection_type}')>"
