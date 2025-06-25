"""
models.py

Database models for the MaLDReTH Infrastructure Interactions application.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()


class Stage(db.Model):
    """
    Represents a stage in the research data lifecycle.
    """
    __tablename__ = 'stages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    categories = db.relationship('ToolCategory', backref='stage', lazy='dynamic', cascade='all, delete-orphan')
    tools = db.relationship('Tool', backref='stage', lazy='dynamic', cascade='all, delete-orphan')
    outgoing_connections = db.relationship('Connection', foreign_keys='Connection.from_stage_id', backref='from_stage', lazy='dynamic', cascade='all, delete-orphan')
    incoming_connections = db.relationship('Connection', foreign_keys='Connection.to_stage_id', backref='to_stage', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Stage '{self.name}'>"


class ToolCategory(db.Model):
    """
    Represents a category of tools within a stage.
    """
    __tablename__ = 'tool_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tools = db.relationship('Tool', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ToolCategory '{self.category}'>"


class Tool(db.Model):
    """
    Represents a specific tool.
    """
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(500))
    provider = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=False)
    stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Tool '{self.name}'>"


class Connection(db.Model):
    """
    Represents a connection between two stages.
    """
    __tablename__ = 'connections'
    
    id = db.Column(db.Integer, primary_key=True)
    from_stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'), nullable=False)
    to_stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'), nullable=False)
    type = db.Column(db.String(50), default='solid')  # 'solid' or 'dashed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Connection '{self.from_stage.name}' -> '{self.to_stage.name}'>"
