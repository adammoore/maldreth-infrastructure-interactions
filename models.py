"""
models.py

Database models for the MaLDReTH Infrastructure Interactions application.
Defines SQLAlchemy models for storing interaction data.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

# Initialize SQLAlchemy (will be configured by app factory)
db = SQLAlchemy()


class Interaction(db.Model):
    """
    Model for storing infrastructure interaction data.
    
    This model represents potential interactions between research infrastructure
    components across the research data lifecycle.
    """
    __tablename__ = 'interactions'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Core interaction data
    interaction_type = Column(String(100), nullable=False, 
                            help_text="Type of interaction (e.g., data_flow, api_call, etc.)")
    source_infrastructure = Column(String(200), nullable=False,
                                 help_text="Source infrastructure component")
    target_infrastructure = Column(String(200), nullable=False,
                                 help_text="Target infrastructure component")
    lifecycle_stage = Column(String(50), nullable=False,
                           help_text="Research data lifecycle stage")
    description = Column(Text, nullable=False,
                        help_text="Detailed description of the interaction")
    
    # Optional technical details
    technical_details = Column(Text, nullable=True,
                             help_text="Technical implementation details")
    benefits = Column(Text, nullable=True,
                     help_text="Benefits of this interaction")
    challenges = Column(Text, nullable=True,
                       help_text="Challenges or limitations")
    examples = Column(Text, nullable=True,
                     help_text="Real-world examples")
    
    # Contact information
    contact_person = Column(String(200), nullable=True,
                          help_text="Contact person name")
    organization = Column(String(200), nullable=True,
                         help_text="Organization name")
    email = Column(String(200), nullable=True,
                  help_text="Contact email address")
    
    # Classification
    priority = Column(String(20), nullable=True, default='medium',
                     help_text="Priority level (high, medium, low)")
    complexity = Column(String(20), nullable=True, default='moderate',
                       help_text="Complexity level (simple, moderate, complex)")
    status = Column(String(20), nullable=True, default='proposed',
                   help_text="Status (proposed, implemented, deprecated)")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False,
                       help_text="When the record was created")
    updated_at = Column(DateTime, default=datetime.utcnow, 
                       onupdate=datetime.utcnow, nullable=False,
                       help_text="When the record was last updated")
    
    def __repr__(self):
        """String representation of the interaction."""
        return f'<Interaction {self.id}: {self.source_infrastructure} -> {self.target_infrastructure}>'
    
    def __str__(self):
        """Human-readable string representation."""
        return f'{self.interaction_type}: {self.source_infrastructure} -> {self.target_infrastructure}'
    
    def to_dict(self):
        """
        Convert the interaction to a dictionary for JSON serialization.
        
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
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an Interaction instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing interaction data
            
        Returns:
            Interaction: New Interaction instance
        """
        # Remove None values and system fields
        clean_data = {k: v for k, v in data.items() 
                     if v is not None and k not in ['id', 'created_at', 'updated_at']}
        
        return cls(**clean_data)
    
    def update_from_dict(self, data):
        """
        Update the interaction from a dictionary.
        
        Args:
            data (dict): Dictionary containing updated interaction data
        """
        updatable_fields = [
            'interaction_type', 'source_infrastructure', 'target_infrastructure',
            'lifecycle_stage', 'description', 'technical_details', 'benefits',
            'challenges', 'examples', 'contact_person', 'organization', 
            'email', 'priority', 'complexity', 'status'
        ]
        
        for field in updatable_fields:
            if field in data and data[field] is not None:
                setattr(self, field, data[field])
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
    
    @property
    def interaction_description(self):
        """Alias for description field for backwards compatibility."""
        return self.description
    
    @staticmethod
    def get_interaction_types():
        """
        Get all available interaction types.
        
        Returns:
            list: List of available interaction types
        """
        return [
            'data_flow', 'api_call', 'file_transfer', 'database_connection',
            'authentication', 'authorization', 'metadata_exchange',
            'workflow_integration', 'service_discovery', 'monitoring',
            'backup_sync', 'user_interface', 'other'
        ]
    
    @staticmethod
    def get_lifecycle_stages():
        """
        Get all available lifecycle stages.
        
        Returns:
            list: List of available lifecycle stages
        """
        return [
            'conceptualise', 'plan', 'collect', 'process', 'analyse',
            'store', 'publish', 'preserve', 'share', 'access', 
            'transform', 'cross_cutting'
        ]
    
    @staticmethod
    def get_priority_levels():
        """
        Get all available priority levels.
        
        Returns:
            list: List of available priority levels
        """
        return ['high', 'medium', 'low']
    
    @staticmethod
    def get_complexity_levels():
        """
        Get all available complexity levels.
        
        Returns:
            list: List of available complexity levels
        """
        return ['simple', 'moderate', 'complex']
    
    @staticmethod
    def get_status_options():
        """
        Get all available status options.
        
        Returns:
            list: List of available status options
        """
        return ['proposed', 'implemented', 'deprecated']
    
    def validate(self):
        """
        Validate the interaction data.
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Required fields
        if not self.interaction_type:
            errors.append("Interaction type is required")
        elif self.interaction_type not in self.get_interaction_types():
            errors.append(f"Invalid interaction type: {self.interaction_type}")
        
        if not self.source_infrastructure:
            errors.append("Source infrastructure is required")
        
        if not self.target_infrastructure:
            errors.append("Target infrastructure is required")
        
        if not self.lifecycle_stage:
            errors.append("Lifecycle stage is required")
        elif self.lifecycle_stage not in self.get_lifecycle_stages():
            errors.append(f"Invalid lifecycle stage: {self.lifecycle_stage}")
        
        if not self.description:
            errors.append("Description is required")
        
        # Optional field validation
        if self.priority and self.priority not in self.get_priority_levels():
            errors.append(f"Invalid priority level: {self.priority}")
        
        if self.complexity and self.complexity not in self.get_complexity_levels():
            errors.append(f"Invalid complexity level: {self.complexity}")
        
        if self.status and self.status not in self.get_status_options():
            errors.append(f"Invalid status: {self.status}")
        
        # Email validation (basic)
        if self.email and '@' not in self.email:
            errors.append("Invalid email address format")
        
        return len(errors) == 0, errors


def create_tables(app):
    """
    Create all database tables.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")


def drop_tables(app):
    """
    Drop all database tables.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        print("Database tables dropped successfully")


def init_database(app):
    """
    Initialize the database with any required seed data.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add any seed data here if needed
        # For now, we'll just ensure the tables exist
        
        print("Database initialized successfully")
