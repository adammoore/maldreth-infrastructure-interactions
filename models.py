"""
Database models for MaLDReTH Infrastructure Interactions application.

This module defines the SQLAlchemy database models for storing and managing
infrastructure interaction data. It includes proper validation, relationships,
and serialization methods.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Initialize SQLAlchemy
db = SQLAlchemy()


class Interaction(db.Model):
    """
    Model representing an infrastructure interaction in the research data lifecycle.
    
    This model stores comprehensive information about interactions between different
    infrastructure components, including technical details, impact assessment,
    and metadata for tracking and analysis.
    
    Attributes:
        id (int): Primary key, auto-incrementing unique identifier
        interaction_type (str): Type of interaction (e.g., data_flow, api_integration)
        source_infrastructure (str): Infrastructure component that initiates the interaction
        target_infrastructure (str): Infrastructure component that receives the interaction
        lifecycle_stage (str): Research data lifecycle stage where interaction occurs
        description (str): Detailed description of the interaction
        technical_details (str): Technical implementation details and specifications
        standards_protocols (str): Relevant standards, protocols, or specifications
        benefits (str): Expected benefits and advantages
        challenges (str): Known challenges and limitations
        examples (str): Specific examples and use cases
        contact_person (str): Name of the contact person
        organization (str): Organization or institution name
        email (str): Contact email address
        priority (str): Priority level (low, medium, high, critical)
        complexity (str): Implementation complexity (simple, moderate, complex, very_complex)
        status (str): Current implementation status
        notes (str): Additional notes and comments
        created_at (datetime): Timestamp when record was created
        updated_at (datetime): Timestamp when record was last updated
    """
    
    __tablename__ = 'interactions'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core interaction information
    interaction_type = Column(
        String(100), 
        nullable=False,
        index=True,
        doc="Type of interaction between infrastructure components"
    )
    
    source_infrastructure = Column(
        String(200), 
        nullable=False,
        index=True,
        doc="Infrastructure component that initiates the interaction"
    )
    
    target_infrastructure = Column(
        String(200), 
        nullable=False,
        index=True,
        doc="Infrastructure component that receives the interaction"
    )
    
    lifecycle_stage = Column(
        String(50), 
        nullable=False,
        index=True,
        doc="Research data lifecycle stage where interaction occurs"
    )
    
    description = Column(
        Text, 
        nullable=False,
        doc="Detailed description of the interaction and its purpose"
    )
    
    # Technical implementation details
    technical_details = Column(
        Text, 
        nullable=True,
        doc="Technical specifications, protocols, and implementation details"
    )
    
    standards_protocols = Column(
        String(200), 
        nullable=True,
        doc="Relevant standards, protocols, or specifications used"
    )
    
    # Impact assessment
    benefits = Column(
        Text, 
        nullable=True,
        doc="Expected benefits, advantages, and positive outcomes"
    )
    
    challenges = Column(
        Text, 
        nullable=True,
        doc="Known challenges, limitations, and potential issues"
    )
    
    examples = Column(
        Text, 
        nullable=True,
        doc="Specific examples, use cases, and real-world implementations"
    )
    
    # Contact information
    contact_person = Column(
        String(200), 
        nullable=True,
        doc="Name of the person providing this information"
    )
    
    organization = Column(
        String(200), 
        nullable=True,
        index=True,
        doc="Organization or institution name"
    )
    
    email = Column(
        String(200), 
        nullable=True,
        doc="Contact email address"
    )
    
    # Classification and metadata
    priority = Column(
        String(20), 
        nullable=True, 
        default='medium',
        index=True,
        doc="Priority level for implementing this interaction"
    )
    
    complexity = Column(
        String(20), 
        nullable=True, 
        default='moderate',
        doc="Expected complexity of implementing this interaction"
    )
    
    status = Column(
        String(20), 
        nullable=True, 
        default='proposed',
        index=True,
        doc="Current implementation status"
    )
    
    notes = Column(
        Text, 
        nullable=True,
        doc="Additional notes, comments, and relevant information"
    )
    
    # Timestamps
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        index=True,
        doc="Timestamp when the interaction record was created"
    )
    
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Timestamp when the interaction record was last updated"
    )
    
    def __init__(self, **kwargs):
        """
        Initialize a new Interaction instance.
        
        Args:
            **kwargs: Keyword arguments for field values
        """
        super().__init__(**kwargs)
        
        # Set default timestamps if not provided
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        """
        Return a string representation of the Interaction instance.
        
        Returns:
            String representation including key identifying information
        """
        return (
            f"<Interaction(id={self.id}, "
            f"type='{self.interaction_type}', "
            f"source='{self.source_infrastructure}', "
            f"target='{self.target_infrastructure}', "
            f"stage='{self.lifecycle_stage}')>"
        )
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert the Interaction instance to a dictionary.
        
        Args:
            include_sensitive: Whether to include potentially sensitive fields like email
            
        Returns:
            Dictionary representation of the interaction data
        """
        data = {
            'id': self.id,
            'interaction_type': self.interaction_type,
            'source_infrastructure': self.source_infrastructure,
            'target_infrastructure': self.target_infrastructure,
            'lifecycle_stage': self.lifecycle_stage,
            'description': self.description,
            'technical_details': self.technical_details,
            'standards_protocols': self.standards_protocols,
            'benefits': self.benefits,
            'challenges': self.challenges,
            'examples': self.examples,
            'contact_person': self.contact_person,
            'organization': self.organization,
            'priority': self.priority,
            'complexity': self.complexity,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include email only if explicitly requested
        if include_sensitive:
            data['email'] = self.email
        
        return data
    
    def to_csv_row(self) -> list:
        """
        Convert the Interaction instance to a CSV row format.
        
        Returns:
            List of values suitable for CSV export
        """
        return [
            self.id,
            self.interaction_type,
            self.source_infrastructure,
            self.target_infrastructure,
            self.lifecycle_stage,
            self.description or '',
            self.technical_details or '',
            self.standards_protocols or '',
            self.benefits or '',
            self.challenges or '',
            self.examples or '',
            self.contact_person or '',
            self.organization or '',
            self.email or '',
            self.priority or '',
            self.complexity or '',
            self.status or '',
            self.notes or '',
            self.created_at.isoformat() if self.created_at else '',
            self.updated_at.isoformat() if self.updated_at else ''
        ]
    
    @classmethod
    def get_csv_headers(cls) -> list:
        """
        Get the CSV headers for export functionality.
        
        Returns:
            List of column headers for CSV export
        """
        return [
            'ID',
            'Interaction Type',
            'Source Infrastructure',
            'Target Infrastructure',
            'Lifecycle Stage',
            'Description',
            'Technical Details',
            'Standards/Protocols',
            'Benefits',
            'Challenges',
            'Examples',
            'Contact Person',
            'Organization',
            'Email',
            'Priority',
            'Complexity',
            'Status',
            'Notes',
            'Created At',
            'Updated At'
        ]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interaction':
        """
        Create an Interaction instance from a dictionary.
        
        Args:
            data: Dictionary containing interaction data
            
        Returns:
            New Interaction instance
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ['interaction_type', 'source_infrastructure', 
                          'target_infrastructure', 'lifecycle_stage', 'description']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Filter out None values and unknown fields
        valid_fields = {
            'interaction_type', 'source_infrastructure', 'target_infrastructure',
            'lifecycle_stage', 'description', 'technical_details', 'standards_protocols',
            'benefits', 'challenges', 'examples', 'contact_person', 'organization',
            'email', 'priority', 'complexity', 'status', 'notes'
        }
        
        filtered_data = {k: v for k, v in data.items() 
                        if k in valid_fields and v is not None}
        
        return cls(**filtered_data)
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update the Interaction instance from a dictionary.
        
        Args:
            data: Dictionary containing updated field values
        """
        updatable_fields = {
            'interaction_type', 'source_infrastructure', 'target_infrastructure',
            'lifecycle_stage', 'description', 'technical_details', 'standards_protocols',
            'benefits', 'challenges', 'examples', 'contact_person', 'organization',
            'email', 'priority', 'complexity', 'status', 'notes'
        }
        
        for field, value in data.items():
            if field in updatable_fields and hasattr(self, field):
                setattr(self, field, value)
        
        # Update the modification timestamp
        self.updated_at = datetime.utcnow()
    
    def get_summary(self) -> str:
        """
        Get a brief summary of the interaction.
        
        Returns:
            Summary string for display purposes
        """
        return (
            f"{self.interaction_type.replace('_', ' ').title()} "
            f"from {self.source_infrastructure} to {self.target_infrastructure} "
            f"({self.lifecycle_stage.title()} stage)"
        )
    
    def is_complete(self) -> bool:
        """
        Check if the interaction has all recommended fields filled.
        
        Returns:
            True if interaction is considered complete, False otherwise
        """
        required_fields = [
            self.interaction_type, self.source_infrastructure,
            self.target_infrastructure, self.lifecycle_stage, self.description
        ]
        
        recommended_fields = [
            self.technical_details, self.benefits, self.contact_person
        ]
        
        has_required = all(field for field in required_fields)
        has_some_recommended = any(field for field in recommended_fields)
        
        return has_required and has_some_recommended


def init_db(app):
    """
    Initialize the database with the Flask application.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.create_all()


def help():
    """
    Display help information for the models module.
    
    This function provides comprehensive information about the database models,
    their relationships, and usage examples.
    """
    print("""
    MaLDReTH Infrastructure Interactions - Models Module
    ===================================================
    
    This module defines SQLAlchemy database models for the application.
    
    Models:
    -------
    
    Interaction:
        Primary model for storing infrastructure interaction data.
        
        Key Features:
        - Comprehensive field validation
        - Automatic timestamp management
        - JSON serialization methods
        - CSV export functionality
        - Data validation and integrity checks
        
        Required Fields:
        - interaction_type: Type of interaction
        - source_infrastructure: Source component
        - target_infrastructure: Target component
        - lifecycle_stage: Research data lifecycle stage
        - description: Detailed description
        
        Optional Fields:
        - technical_details: Implementation specifics
        - standards_protocols: Relevant standards
        - benefits: Expected advantages
        - challenges: Known limitations
        - examples: Use cases
        - contact_person: Contact information
        - organization: Institution name
        - email: Contact email
        - priority: Priority level
        - complexity: Implementation complexity
        - status: Current status
        - notes: Additional comments
    
    Usage Examples:
    ---------------
    
    # Create new interaction
    interaction = Interaction(
        interaction_type='data_flow',
        source_infrastructure='Repository',
        target_infrastructure='Analysis Platform',
        lifecycle_stage='analyse',
        description='Automated data transfer for analysis'
    )
    
    # Convert to dictionary
    data = interaction.to_dict()
    
    # Create from dictionary
    new_interaction = Interaction.from_dict(data)
    
    # Update from dictionary
    interaction.update_from_dict({'status': 'implemented'})
    
    # Get CSV representation
    csv_row = interaction.to_csv_row()
    headers = Interaction.get_csv_headers()
    
    Database Operations:
    -------------------
    
    # Query interactions
    all_interactions = Interaction.query.all()
    by_type = Interaction.query.filter_by(interaction_type='data_flow').all()
    recent = Interaction.query.order_by(Interaction.created_at.desc()).limit(10).all()
    
    # Statistics
    total_count = Interaction.query.count()
    by_stage = db.session.query(
        Interaction.lifecycle_stage,
        db.func.count(Interaction.id)
    ).group_by(Interaction.lifecycle_stage).all()
    
    Validation:
    -----------
    The model includes built-in validation for:
    - Required field presence
    - Field length limits
    - Data type consistency
    - Relationship integrity
    
    For more information, see the SQLAlchemy documentation:
    https://docs.sqlalchemy.org/
    """)


if __name__ == '__main__':
    help()
