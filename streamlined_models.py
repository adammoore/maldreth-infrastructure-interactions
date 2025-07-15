"""
streamlined_models.py
Refactored database models for MaLDReTH tool interaction capture.

This module defines SQLAlchemy models aligned with the RDA-OfSR WG outputs,
including a detailed ToolInteraction model and comprehensive ExemplarTool fields.
"""

from datetime import datetime
from extensions import db


class MaldrethStage(db.Model):
    """Model representing stages in the MaLDReTH cycle."""
    __tablename__ = 'maldreth_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#007bff')
    position = db.Column(db.Integer, default=0)
    
    tools = db.relationship('ExemplarTool', backref='stage', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'position': self.position
        }


class ExemplarTool(db.Model):
    """Model representing exemplar tools within each MaLDReTH stage."""
    __tablename__ = 'exemplar_tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    stage_id = db.Column(db.Integer, db.ForeignKey('maldreth_stages.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    source_interactions = db.relationship(
        'ToolInteraction',
        foreign_keys='ToolInteraction.source_tool_id',
        backref='source_tool',
        lazy='dynamic'
    )
    target_interactions = db.relationship(
        'ToolInteraction',
        foreign_keys='ToolInteraction.target_tool_id',
        backref='target_tool',
        lazy='dynamic'
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'stage': self.stage.name if self.stage else None,
            'is_active': self.is_active
        }


class ToolInteraction(db.Model):
    """Model representing interactions between tools, aligned with the Google Sheet fields."""
    __tablename__ = 'tool_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core interaction data
    source_tool_id = db.Column(db.Integer, db.ForeignKey('exemplar_tools.id'), nullable=False)
    target_tool_id = db.Column(db.Integer, db.ForeignKey('exemplar_tools.id'), nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False)
    lifecycle_stage = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Technical details
    technical_details = db.Column(db.Text)
    benefits = db.Column(db.Text)
    challenges = db.Column(db.Text)
    examples = db.Column(db.Text)
    
    # Contact information
    contact_person = db.Column(db.String(100))
    organization = db.Column(db.String(100))
    email = db.Column(db.String(100))
    
    # Classification
    priority = db.Column(db.String(20))
    complexity = db.Column(db.String(20))
    status = db.Column(db.String(20))
    
    # Submission metadata
    submitted_by = db.Column(db.String(100))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_tool': self.source_tool.to_dict() if self.source_tool else None,
            'target_tool': self.target_tool.to_dict() if self.target_tool else None,
            'interaction_type': self.interaction_type,
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
            'submitted_by': self.submitted_by,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
