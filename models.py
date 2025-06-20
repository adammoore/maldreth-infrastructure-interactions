"""
Database models for the MaLDReTH Infrastructure Interactions application.

This module defines the SQLAlchemy models for representing infrastructure
interactions and their properties in the database.
"""

from datetime import datetime
from app import db

class Interaction(db.Model):
    """
    Model representing an infrastructure interaction in the research data lifecycle.
    
    This model captures information about how different pieces of research
    infrastructure interact with each other throughout the data lifecycle.
    
    Attributes:
        id (int): Primary key of the interaction
        interaction_type (str): Type of interaction (e.g., 'data_flow', 'api_call', 'file_transfer')
        source_infrastructure (str): Source infrastructure component
        target_infrastructure (str): Target infrastructure component
        lifecycle_stage (str): Stage in the research data lifecycle
        description (str): Detailed description of the interaction
        technical_details (str): Technical implementation details
        benefits (str): Benefits of this interaction
        challenges (str): Challenges or limitations
        examples (str): Examples of this interaction in practice
        contact_person (str): Contact person for this interaction
        organization (str): Organization associated with the interaction
        email (str): Contact email address
        priority (str): Priority level ('high', 'medium', 'low')
        complexity (str): Complexity level ('simple', 'moderate', 'complex')
        status (str): Current status ('proposed', 'implemented', 'deprecated')
        created_at (datetime): When the interaction was recorded
        updated_at (datetime): When the interaction was last updated
    """
    __tablename__ = 'interactions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Core interaction information
    interaction_type = db.Column(db.String(100), nullable=False, index=True)
    source_infrastructure = db.Column(db.String(200), nullable=False, index=True)
    target_infrastructure = db.Column(db.String(200), nullable=False, index=True)
    lifecycle_stage = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    
    # Technical details
    technical_details = db.Column(db.Text)
    benefits = db.Column(db.Text)
    challenges = db.Column(db.Text)
    examples = db.Column(db.Text)
    
    # Contact information
    contact_person = db.Column(db.String(200))
    organization = db.Column(db.String(200))
    email = db.Column(db.String(254))  # RFC 5321 email length limit
    
    # Classification
    priority = db.Column(db.String(20), default='medium')  # 'high', 'medium', 'low'
    complexity = db.Column(db.String(20), default='moderate')  # 'simple', 'moderate', 'complex'
    status = db.Column(db.String(20), default='proposed')  # 'proposed', 'implemented', 'deprecated'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        db.Index('ix_interaction_stage_type', 'lifecycle_stage', 'interaction_type'),
        db.Index('ix_infrastructure_pair', 'source_infrastructure', 'target_infrastructure'),
        db.Index('ix_status_priority', 'status', 'priority'),
    )
    
    def __init__(self, **kwargs):
        """
        Initialize a new Interaction instance.
        
        Args:
            **kwargs: Keyword arguments for interaction attributes
        """
        super(Interaction, self).__init__(**kwargs)
        
        # Validate interaction type
        valid_types = [
            'data_flow', 'api_call', 'file_transfer', 'database_connection',
            'authentication', 'authorization', 'metadata_exchange',
            'workflow_integration', 'service_discovery', 'monitoring',
            'backup_sync', 'user_interface', 'other'
        ]
        
        if self.interaction_type and self.interaction_type not in valid_types:
            # Log warning but don't raise error to allow flexibility
            import logging
            logging.getLogger(__name__).warning(
                f"Unknown interaction type: {self.interaction_type}"
            )
        
        # Validate lifecycle stage
        valid_stages = [
            'conceptualise', 'plan', 'collect', 'process', 'analyse',
            'store', 'publish', 'preserve', 'share', 'access', 'transform',
            'cross_cutting'  # For interactions that span multiple stages
        ]
        
        if self.lifecycle_stage and self.lifecycle_stage.lower() not in valid_stages:
            import logging
            logging.getLogger(__name__).warning(
                f"Unknown lifecycle stage: {self.lifecycle_stage}"
            )
    
    def to_dict(self):
        """
        Convert the interaction to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the interaction
        """
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
    
    def to_csv_row(self):
        """
        Convert the interaction to a CSV row format.
        
        Returns:
            list: List of values suitable for CSV export
        """
        return [
            self.id,
            self.interaction_type,
            self.source_infrastructure,
            self.target_infrastructure,
            self.lifecycle_stage,
            self.description,
            self.technical_details or '',
            self.benefits or '',
            self.challenges or '',
            self.examples or '',
            self.contact_person or '',
            self.organization or '',
            self.email or '',
            self.priority or '',
            self.complexity or '',
            self.status or '',
            self.created_at.isoformat() if self.created_at else ''
        ]
    
    @classmethod
    def get_interaction_types(cls):
        """
        Get all available interaction types.
        
        Returns:
            list: List of valid interaction types
        """
        return [
            'data_flow', 'api_call', 'file_transfer', 'database_connection',
            'authentication', 'authorization', 'metadata_exchange',
            'workflow_integration', 'service_discovery', 'monitoring',
            'backup_sync', 'user_interface', 'other'
        ]
    
    @classmethod
    def get_lifecycle_stages(cls):
        """
        Get all available lifecycle stages.
        
        Returns:
            list: List of valid lifecycle stages
        """
        return [
            'conceptualise', 'plan', 'collect', 'process', 'analyse',
            'store', 'publish', 'preserve', 'share', 'access', 
            'transform', 'cross_cutting'
        ]
    
    @classmethod
    def get_priority_levels(cls):
        """
        Get all available priority levels.
        
        Returns:
            list: List of valid priority levels
        """
        return ['high', 'medium', 'low']
    
    @classmethod
    def get_complexity_levels(cls):
        """
        Get all available complexity levels.
        
        Returns:
            list: List of valid complexity levels
        """
        return ['simple', 'moderate', 'complex']
    
    @classmethod
    def get_status_options(cls):
        """
        Get all available status options.
        
        Returns:
            list: List of valid status options
        """
        return ['proposed', 'implemented', 'deprecated']
    
    def __repr__(self):
        """
        String representation of the interaction.
        
        Returns:
            str: String representation
        """
        return (f"<Interaction(id={self.id}, type='{self.interaction_type}', "
                f"source='{self.source_infrastructure}', "
                f"target='{self.target_infrastructure}', "
                f"stage='{self.lifecycle_stage}')>")

# Create database tables if they don't exist
def init_db():
    """Initialize database tables."""
    db.create_all()
