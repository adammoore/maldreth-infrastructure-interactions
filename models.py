"""
Database models for the MaLDReTH Research Data Lifecycle Visualization application.

This module defines SQLAlchemy models for managing lifecycle stages, tool categories,
tools, and infrastructure interactions in the research data lifecycle.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, CheckConstraint

db = SQLAlchemy()


class LifecycleStage(db.Model):
    """
    Model representing a stage in the research data lifecycle.
    
    Each stage represents a major phase in the research data lifecycle such as
    Conceptualise, Plan, Collect, Process, Analyse, etc.
    """
    
    __tablename__ = 'lifecycle_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # MaLDReTH specific fields
    maldreth_description = db.Column(db.Text)
    color_code = db.Column(db.String(7))  # Hex color code
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    tool_categories = db.relationship('ToolCategory', backref='stage', lazy='dynamic', cascade='all, delete-orphan')
    tools = db.relationship('Tool', backref='stage', lazy='dynamic', cascade='all, delete-orphan')
    substages = db.relationship('LifecycleSubstage', backref='stage', lazy='dynamic', cascade='all, delete-orphan')
    
    # Stage connections (from this stage)
    outgoing_connections = db.relationship(
        'StageConnection', 
        foreign_keys='StageConnection.from_stage_id',
        backref='from_stage', 
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Stage connections (to this stage)
    incoming_connections = db.relationship(
        'StageConnection',
        foreign_keys='StageConnection.to_stage_id', 
        backref='to_stage',
        lazy='dynamic'
    )
    
    # Infrastructure interactions
    infrastructure_interactions = db.relationship(
        'InfrastructureInteraction',
        backref='lifecycle_stage',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Add index for performance
    __table_args__ = (
        Index('idx_lifecycle_stage_order', 'order'),
        Index('idx_lifecycle_stage_name', 'name'),
        CheckConstraint('order >= 0', name='check_positive_order'),
    )

    def __repr__(self):
        return f'<LifecycleStage {self.name}>'

    def to_dict(self):
        """Convert the stage to a dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'maldreth_description': self.maldreth_description,
            'order': self.order,
            'color_code': self.color_code,
            'icon': self.icon,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class LifecycleSubstage(db.Model):
    """
    Model representing a substage within a lifecycle stage.
    
    Substages are more specific phases or activities within a lifecycle stage.
    """
    
    __tablename__ = 'lifecycle_substages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    is_exemplar = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tools = db.relationship('Tool', backref='substage', lazy='dynamic')
    
    # Add index for performance
    __table_args__ = (
        Index('idx_substage_stage_order', 'stage_id', 'order'),
        Index('idx_substage_name', 'name'),
    )

    def __repr__(self):
        return f'<LifecycleSubstage {self.name}>'

    def to_dict(self):
        """Convert the substage to a dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stage_id': self.stage_id,
            'order': self.order,
            'is_exemplar': self.is_exemplar,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ToolCategory(db.Model):
    """
    Model representing a category of tools within a lifecycle stage.
    
    Tool categories group related tools together for better organization.
    """
    
    __tablename__ = 'tool_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    order = db.Column(db.Integer, default=0)  # Made optional with default
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tools = db.relationship('Tool', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    research_tools = db.relationship('ResearchTool', backref='category', lazy='dynamic')
    
    # Add index for performance
    __table_args__ = (
        Index('idx_tool_category_stage_order', 'stage_id', 'order'),
        Index('idx_tool_category_name', 'name'),
        db.UniqueConstraint('name', 'stage_id', name='uq_tool_category_stage'),
    )

    def __repr__(self):
        return f'<ToolCategory {self.name}>'

    def to_dict(self):
        """Convert the tool category to a dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stage_id': self.stage_id,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Tool(db.Model):
    """
    Model representing a specific tool used in the research data lifecycle.
    
    Tools are specific software, platforms, or services that researchers use
    during various stages of the data lifecycle.
    """
    
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    provider = db.Column(db.String(200))
    tool_type = db.Column(db.String(200))
    source_type = db.Column(db.String(20))  # 'open', 'closed', 'mixed'
    scope = db.Column(db.String(100))  # 'generic', 'disciplinary'
    is_interoperable = db.Column(db.Boolean, default=False)
    characteristics = db.Column(db.Text)
    
    # Foreign keys
    stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=True)
    substage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_substages.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=True)
    
    # Additional fields
    is_featured = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    order = db.Column(db.Integer, default=0)  # Added order field for consistency
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add index for performance
    __table_args__ = (
        Index('idx_tool_name', 'name'),
        Index('idx_tool_stage_category', 'stage_id', 'category_id'),
        Index('idx_tool_featured', 'is_featured'),
        Index('idx_tool_usage', 'usage_count'),
    )

    def __repr__(self):
        return f'<Tool {self.name}>'

    def to_dict(self):
        """Convert the tool to a dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'provider': self.provider,
            'tool_type': self.tool_type,
            'source_type': self.source_type,
            'scope': self.scope,
            'is_interoperable': self.is_interoperable,
            'characteristics': self.characteristics,
            'stage_id': self.stage_id,
            'substage_id': self.substage_id,
            'category_id': self.category_id,
            'is_featured': self.is_featured,
            'usage_count': self.usage_count,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StageConnection(db.Model):
    """
    Model representing connections between lifecycle stages.
    
    Defines how stages are connected in the lifecycle flow.
    """
    
    __tablename__ = 'stage_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    from_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    to_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    connection_type = db.Column(db.String(50), default='normal')  # 'normal', 'alternative', 'feedback'
    description = db.Column(db.Text)
    weight = db.Column(db.Float, default=1.0)  # For visualization purposes
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add index for performance
    __table_args__ = (
        Index('idx_stage_connection_from_to', 'from_stage_id', 'to_stage_id'),
        Index('idx_stage_connection_type', 'connection_type'),
        db.UniqueConstraint('from_stage_id', 'to_stage_id', name='uq_stage_connection'),
        CheckConstraint('from_stage_id != to_stage_id', name='check_no_self_connection'),
    )

    def __repr__(self):
        return f'<StageConnection {self.from_stage_id}->{self.to_stage_id}>'

    def to_dict(self):
        """Convert the stage connection to a dictionary representation."""
        return {
            'id': self.id,
            'from_stage_id': self.from_stage_id,
            'to_stage_id': self.to_stage_id,
            'connection_type': self.connection_type,
            'description': self.description,
            'weight': self.weight,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class InfrastructureInteraction(db.Model):
    """
    Model representing interactions between research infrastructure components.
    
    Tracks how different infrastructure systems interact within the research lifecycle.
    """
    
    __tablename__ = 'infrastructure_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    interaction_type = db.Column(db.String(100), nullable=False)
    source_system = db.Column(db.String(100), nullable=False)
    target_system = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')  # 'active', 'planned', 'deprecated'
    lifecycle_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add index for performance
    __table_args__ = (
        Index('idx_infra_interaction_type', 'interaction_type'),
        Index('idx_infra_interaction_status', 'status'),
        Index('idx_infra_interaction_systems', 'source_system', 'target_system'),
    )

    def __repr__(self):
        return f'<InfrastructureInteraction {self.source_system}->{self.target_system}>'

    def to_dict(self):
        """Convert the infrastructure interaction to a dictionary representation."""
        return {
            'id': self.id,
            'interaction_type': self.interaction_type,
            'source_system': self.source_system,
            'target_system': self.target_system,
            'description': self.description,
            'status': self.status,
            'lifecycle_stage_id': self.lifecycle_stage_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ResearchTool(db.Model):
    """
    Model representing research tools with additional metadata.
    
    Extended model for research tools with more detailed characteristics.
    """
    
    __tablename__ = 'research_tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    provider = db.Column(db.String(200))
    tool_type = db.Column(db.String(100))
    source_type = db.Column(db.String(50))  # 'open', 'closed', 'mixed'
    scope = db.Column(db.String(100))  # 'generic', 'disciplinary'
    interoperable = db.Column(db.String(50))  # 'yes', 'no', 'partial'
    characteristics = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add index for performance
    __table_args__ = (
        Index('idx_research_tool_name', 'name'),
        Index('idx_research_tool_type', 'tool_type'),
        Index('idx_research_tool_category', 'category_id'),
    )

    def __repr__(self):
        return f'<ResearchTool {self.name}>'

    def to_dict(self):
        """Convert the research tool to a dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'provider': self.provider,
            'tool_type': self.tool_type,
            'source_type': self.source_type,
            'scope': self.scope,
            'interoperable': self.interoperable,
            'characteristics': self.characteristics,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Interaction(db.Model):
    """
    Model representing detailed infrastructure interactions.
    
    More comprehensive model for tracking infrastructure interactions with
    detailed metadata and contact information.
    """
    
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    interaction_type = db.Column(db.String(100), nullable=False)
    source_infrastructure = db.Column(db.String(200), nullable=False)
    target_infrastructure = db.Column(db.String(200), nullable=False)
    lifecycle_stage = db.Column(db.String(100))
    description = db.Column(db.Text)
    technical_details = db.Column(db.Text)
    benefits = db.Column(db.Text)
    challenges = db.Column(db.Text)
    examples = db.Column(db.Text)
    contact_person = db.Column(db.String(200))
    organization = db.Column(db.String(200))
    email = db.Column(db.String(254))  # RFC 5321 email length limit
    priority = db.Column(db.String(20), default='medium')  # 'high', 'medium', 'low'
    complexity = db.Column(db.String(20), default='medium')  # 'high', 'medium', 'low'
    status = db.Column(db.String(20), default='active')  # 'active', 'planned', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add index for performance
    __table_args__ = (
        Index('idx_interaction_type', 'interaction_type'),
        Index('idx_interaction_lifecycle', 'lifecycle_stage'),
        Index('idx_interaction_status', 'status'),
        Index('idx_interaction_priority', 'priority'),
        Index('idx_interaction_infrastructures', 'source_infrastructure', 'target_infrastructure'),
    )

    def __repr__(self):
        return f'<Interaction {self.source_infrastructure}->{self.target_infrastructure}>'

    def to_dict(self):
        """Convert the interaction to a dictionary representation."""
        return {
            'id': self.id,
            'interaction_type': self.interaction_type,
            'source_infrastructure': self.source_infrastructure,
            'target_infrastructure': self.target_infrastructure,
            'lifecycle_stage': self.lifecycle_stage,
            'description': self.description,
            'technical_details': self.technical_details,
            'benefits': self.benefits,
            'challenges': self.challenges,
            'examples': self.examples,
            'contact_person': self.contact_person,
            'organization': self.organization,
            'email': self.email,
            'priority': self.priority,
            'complexity': self.complexity,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
