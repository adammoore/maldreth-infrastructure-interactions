"""
Enhanced database models for Phase 2 MaLDReTH Integration.

This module extends the existing models to integrate with MaLDReTH 1 data,
including lifecycle stages, substages, tools, and their relationships.
"""

from datetime import datetime
from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import and_, or_, func

class LifecycleStage(db.Model):
    """
    Enhanced lifecycle stage model integrating MaLDReTH definitions.
    
    Attributes:
        id (int): Primary key
        name (str): Stage name (e.g., 'Conceptualise', 'Plan')
        description (str): Brief description
        maldreth_description (str): Official MaLDReTH definition
        order (int): Order in the lifecycle (1-12)
        color_code (str): Hex color for visualization
        icon (str): Icon identifier for UI
        is_active (bool): Whether stage is currently active
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = 'lifecycle_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=False)
    maldreth_description = db.Column(db.Text)  # Official MaLDReTH definition
    order = db.Column(db.Integer, nullable=False, unique=True)
    color_code = db.Column(db.String(7), default='#007bff')  # Hex color
    icon = db.Column(db.String(50), default='bi-circle')  # Bootstrap icon
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    substages = db.relationship('LifecycleSubstage', backref='stage', lazy='dynamic', 
                               cascade='all, delete-orphan')
    tool_categories = db.relationship('ToolCategory', backref='stage', lazy='dynamic',
                                    cascade='all, delete-orphan')
    tools = db.relationship('Tool', backref='stage', lazy='dynamic')
    
    # Stage connections
    outgoing_connections = db.relationship('StageConnection', 
                                         foreign_keys='StageConnection.from_stage_id',
                                         backref='from_stage', lazy='dynamic')
    incoming_connections = db.relationship('StageConnection',
                                         foreign_keys='StageConnection.to_stage_id', 
                                         backref='to_stage', lazy='dynamic')
    
    # Interactions
    interactions_as_source = db.relationship('Interaction', 
                                           foreign_keys='Interaction.source_stage_id',
                                           backref='source_stage', lazy='dynamic')
    interactions_as_target = db.relationship('Interaction',
                                           foreign_keys='Interaction.target_stage_id', 
                                           backref='target_stage', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        db.Index('ix_stage_order_active', 'order', 'is_active'),
    )
    
    @hybrid_property
    def tool_count(self):
        """Get the total number of tools for this stage."""
        return self.tools.count()
    
    @hybrid_property
    def substage_count(self):
        """Get the number of substages for this stage."""
        return self.substages.count()
    
    @hybrid_property
    def interaction_count(self):
        """Get the total number of interactions involving this stage."""
        return (self.interactions_as_source.count() + 
                self.interactions_as_target.count())
    
    def get_next_stage(self):
        """Get the next stage in the lifecycle order."""
        return LifecycleStage.query.filter(
            LifecycleStage.order > self.order,
            LifecycleStage.is_active == True
        ).order_by(LifecycleStage.order).first()
    
    def get_previous_stage(self):
        """Get the previous stage in the lifecycle order."""
        return LifecycleStage.query.filter(
            LifecycleStage.order < self.order,
            LifecycleStage.is_active == True
        ).order_by(LifecycleStage.order.desc()).first()
    
    def to_dict(self, include_counts=False):
        """Convert stage to dictionary representation."""
        data = {
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
        
        if include_counts:
            data.update({
                'tool_count': self.tool_count,
                'substage_count': self.substage_count,
                'interaction_count': self.interaction_count
            })
        
        return data
    
    def __repr__(self):
        return f"<LifecycleStage(name='{self.name}', order={self.order})>"

class LifecycleSubstage(db.Model):
    """
    Substages within each lifecycle stage.
    
    Attributes:
        id (int): Primary key
        name (str): Substage name
        description (str): Detailed description
        stage_id (int): Foreign key to parent stage
        order (int): Order within the stage
        is_exemplar (bool): Whether this is an exemplar substage
        created_at (datetime): Creation timestamp
    """
    __tablename__ = 'lifecycle_substages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    is_exemplar = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tools = db.relationship('Tool', backref='substage', lazy='dynamic')
    interactions = db.relationship('Interaction', backref='substage', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        db.Index('ix_substage_stage_order', 'stage_id', 'order'),
        db.UniqueConstraint('stage_id', 'name', name='uq_substage_name_per_stage'),
    )
    
    @hybrid_property
    def tool_count(self):
        """Get the number of tools for this substage."""
        return self.tools.count()
    
    def to_dict(self):
        """Convert substage to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stage_id': self.stage_id,
            'stage_name': self.stage.name if self.stage else None,
            'order': self.order,
            'is_exemplar': self.is_exemplar,
            'tool_count': self.tool_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<LifecycleSubstage(name='{self.name}', stage_id={self.stage_id})>"

class ToolCategory(db.Model):
    """
    Tool categories for classification within stages.
    
    Attributes:
        id (int): Primary key
        name (str): Category name
        description (str): Category description
        stage_id (int): Foreign key to lifecycle stage
        order (int): Display order within stage
        created_at (datetime): Creation timestamp
    """
    __tablename__ = 'tool_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tools = db.relationship('Tool', backref='category', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        db.Index('ix_category_stage_order', 'stage_id', 'order'),
        db.UniqueConstraint('stage_id', 'name', name='uq_category_name_per_stage'),
    )
    
    @hybrid_property
    def tool_count(self):
        """Get the number of tools in this category."""
        return self.tools.count()
    
    def to_dict(self):
        """Convert category to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stage_id': self.stage_id,
            'stage_name': self.stage.name if self.stage else None,
            'order': self.order,
            'tool_count': self.tool_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<ToolCategory(name='{self.name}', stage_id={self.stage_id})>"

class Tool(db.Model):
    """
    Enhanced tool model with MaLDReTH classifications.
    
    Attributes:
        id (int): Primary key
        name (str): Tool name
        description (str): Tool description
        url (str): Tool website URL
        provider (str): Tool provider/creator
        tool_type (str): MaLDReTH tool type classification
        source_type (str): Open/closed source classification
        scope (str): Generic/disciplinary scope
        is_interoperable (bool): Interoperability capability
        characteristics (str): Additional characteristics
        stage_id (int): Primary lifecycle stage
        substage_id (int): Optional specific substage
        category_id (int): Tool category classification
        is_featured (bool): Whether tool is featured/recommended
        usage_count (int): Number of times referenced
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    provider = db.Column(db.String(200), index=True)
    
    # MaLDReTH specific classifications
    tool_type = db.Column(db.String(200), index=True)  # From MaLDReTH categorization
    source_type = db.Column(db.String(20), default='unknown')  # 'open', 'closed', 'freemium', 'unknown'
    scope = db.Column(db.String(100), default='generic')  # 'generic', 'disciplinary'
    is_interoperable = db.Column(db.Boolean, default=False)
    characteristics = db.Column(db.Text)  # Additional tool characteristics
    
    # Relationships
    stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    substage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_substages.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'))
    
    # Metadata
    is_featured = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many with interactions
    interactions = db.relationship('InteractionTool', backref='tool', lazy='dynamic',
                                 cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('ix_tool_stage_category', 'stage_id', 'category_id'),
        db.Index('ix_tool_type_scope', 'tool_type', 'scope'),
        db.Index('ix_tool_source_interop', 'source_type', 'is_interoperable'),
        db.Index('ix_tool_usage_featured', 'usage_count', 'is_featured'),
    )
    
    @classmethod
    def get_source_types(cls):
        """Get all available source types."""
        return ['open', 'closed', 'freemium', 'unknown']
    
    @classmethod
    def get_scope_types(cls):
        """Get all available scope types."""
        return ['generic', 'disciplinary']
    
    @classmethod
    def search(cls, query, stage_id=None, category_id=None, source_type=None, 
               is_interoperable=None, limit=50):
        """
        Advanced tool search with filters.
        
        Args:
            query (str): Search query for name/description
            stage_id (int): Filter by lifecycle stage
            category_id (int): Filter by tool category
            source_type (str): Filter by source type
            is_interoperable (bool): Filter by interoperability
            limit (int): Maximum results to return
            
        Returns:
            Query: SQLAlchemy query object
        """
        q = cls.query
        
        if query:
            q = q.filter(or_(
                cls.name.ilike(f'%{query}%'),
                cls.description.ilike(f'%{query}%'),
                cls.provider.ilike(f'%{query}%')
            ))
        
        if stage_id:
            q = q.filter(cls.stage_id == stage_id)
            
        if category_id:
            q = q.filter(cls.category_id == category_id)
            
        if source_type:
            q = q.filter(cls.source_type == source_type)
            
        if is_interoperable is not None:
            q = q.filter(cls.is_interoperable == is_interoperable)
        
        return q.order_by(cls.usage_count.desc(), cls.name).limit(limit)
    
    def increment_usage(self):
        """Increment the usage count for this tool."""
        self.usage_count += 1
        db.session.commit()
    
    def to_dict(self, include_relationships=False):
        """Convert tool to dictionary representation."""
        data = {
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relationships:
            data.update({
                'stage_name': self.stage.name if self.stage else None,
                'substage_name': self.substage.name if self.substage else None,
                'category_name': self.category.name if self.category else None
            })
        
        return data
    
    def __repr__(self):
        return f"<Tool(name='{self.name}', provider='{self.provider}')>"

class Interaction(db.Model):
    """
    Enhanced interaction model with stage/substage relationships.
    
    This extends the original interaction model to integrate with
    MaLDReTH lifecycle stages, substages, and tools.
    """
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core interaction information
    interaction_type = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    
    # Enhanced relationships to MaLDReTH data
    source_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'))
    target_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'))
    substage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_substages.id'))
    
    # Infrastructure information (backward compatibility)
    source_infrastructure = db.Column(db.String(200), nullable=False, index=True)
    target_infrastructure = db.Column(db.String(200), nullable=False, index=True)
    lifecycle_stage = db.Column(db.String(100), index=True)  # Legacy field
    
    # Technical details
    technical_details = db.Column(db.Text)
    benefits = db.Column(db.Text)
    challenges = db.Column(db.Text)
    examples = db.Column(db.Text)
    
    # Contact information
    contact_person = db.Column(db.String(200))
    organization = db.Column(db.String(200), index=True)
    email = db.Column(db.String(254))
    
    # Classification
    priority = db.Column(db.String(20), default='medium', index=True)
    complexity = db.Column(db.String(20), default='moderate', index=True)
    status = db.Column(db.String(20), default='proposed', index=True)
    
    # Metadata
    is_validated = db.Column(db.Boolean, default=False)
    validation_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many with tools
    tools = db.relationship('InteractionTool', backref='interaction', lazy='dynamic',
                          cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('ix_interaction_stages', 'source_stage_id', 'target_stage_id'),
        db.Index('ix_interaction_classification', 'priority', 'complexity', 'status'),
        db.Index('ix_interaction_created', 'created_at'),
        db.Index('ix_interaction_validation', 'is_validated'),
    )
    
    @classmethod
    def get_interaction_types(cls):
        """Get all available interaction types."""
        return [
            'data_flow', 'api_call', 'file_transfer', 'database_connection',
            'authentication', 'authorization', 'metadata_exchange',
            'workflow_integration', 'service_discovery', 'monitoring',
            'backup_sync', 'user_interface', 'notification', 'reporting', 'other'
        ]
    
    def add_tool(self, tool_id, role='involved'):
        """
        Add a tool to this interaction.
        
        Args:
            tool_id (int): ID of the tool to add
            role (str): Role of the tool ('source', 'target', 'facilitator', 'involved')
        """
        existing = InteractionTool.query.filter_by(
            interaction_id=self.id, 
            tool_id=tool_id
        ).first()
        
        if not existing:
            interaction_tool = InteractionTool(
                interaction_id=self.id,
                tool_id=tool_id,
                role=role
            )
            db.session.add(interaction_tool)
            
            # Increment tool usage count
            tool = Tool.query.get(tool_id)
            if tool:
                tool.increment_usage()
    
    def get_tool_list(self):
        """Get list of tools associated with this interaction."""
        return [it.tool for it in self.tools if it.tool]
    
    def to_dict(self, include_tools=False):
        """Convert interaction to dictionary representation."""
        data = {
            'id': self.id,
            'interaction_type': self.interaction_type,
            'description': self.description,
            'source_stage_id': self.source_stage_id,
            'target_stage_id': self.target_stage_id,
            'substage_id': self.substage_id,
            'source_infrastructure': self.source_infrastructure,
            'target_infrastructure': self.target_infrastructure,
            'lifecycle_stage': self.lifecycle_stage,
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
            'is_validated': self.is_validated,
            'validation_notes': self.validation_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_tools:
            data['tools'] = [
                {
                    'tool': tool.tool.to_dict() if tool.tool else None,
                    'role': tool.role
                }
                for tool in self.tools
            ]
        
        return data
    
    def __repr__(self):
        return (f"<Interaction(type='{self.interaction_type}', "
                f"source='{self.source_infrastructure}', "
                f"target='{self.target_infrastructure}')>")

class InteractionTool(db.Model):
    """
    Many-to-many relationship between interactions and tools.
    
    Attributes:
        id (int): Primary key
        interaction_id (int): Foreign key to interaction
        tool_id (int): Foreign key to tool
        role (str): Role of tool in interaction
        notes (str): Additional notes about tool's role
        created_at (datetime): When relationship was created
    """
    __tablename__ = 'interaction_tools'
    
    id = db.Column(db.Integer, primary_key=True)
    interaction_id = db.Column(db.Integer, db.ForeignKey('interactions.id'), nullable=False)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    role = db.Column(db.String(50), default='involved')  # 'source', 'target', 'facilitator', 'involved'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('interaction_id', 'tool_id', name='uq_interaction_tool'),
        db.Index('ix_interaction_tool_role', 'role'),
    )
    
    @classmethod
    def get_role_types(cls):
        """Get all available role types."""
        return ['source', 'target', 'facilitator', 'involved']
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'interaction_id': self.interaction_id,
            'tool_id': self.tool_id,
            'role': self.role,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<InteractionTool(interaction_id={self.interaction_id}, tool_id={self.tool_id}, role='{self.role}')>"

class StageConnection(db.Model):
    """
    Connections between lifecycle stages.
    
    Attributes:
        id (int): Primary key
        from_stage_id (int): Source stage ID
        to_stage_id (int): Target stage ID
        connection_type (str): Type of connection
        description (str): Description of the connection
        weight (float): Connection strength/frequency
        is_active (bool): Whether connection is currently active
        created_at (datetime): Creation timestamp
    """
    __tablename__ = 'stage_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    from_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    to_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    connection_type = db.Column(db.String(50), default='normal', index=True)  # 'normal', 'alternative', 'feedback'
    description = db.Column(db.Text)
    weight = db.Column(db.Float, default=1.0)  # For visualization
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('from_stage_id != to_stage_id', name='no_self_connection'),
        db.UniqueConstraint('from_stage_id', 'to_stage_id', name='unique_stage_connection'),
        db.Index('ix_connection_type_active', 'connection_type', 'is_active'),
    )
    
    @classmethod
    def get_connection_types(cls):
        """Get all available connection types."""
        return ['normal', 'alternative', 'feedback', 'optional']
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'from_stage_id': self.from_stage_id,
            'to_stage_id': self.to_stage_id,
            'from_stage_name': self.from_stage.name if self.from_stage else None,
            'to_stage_name': self.to_stage.name if self.to_stage else None,
            'connection_type': self.connection_type,
            'description': self.description,
            'weight': self.weight,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return (f"<StageConnection(from={self.from_stage_id}, "
                f"to={self.to_stage_id}, type='{self.connection_type}')>")

# Migration helper functions
def init_maldreth_data():
    """Initialize database with MaLDReTH lifecycle stages and basic structure."""
    
    # Official MaLDReTH lifecycle stages
    stages_data = [
        {
            'name': 'Conceptualise',
            'description': 'Formulate research ideas and define data requirements',
            'maldreth_description': 'To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.',
            'order': 1,
            'color_code': '#e74c3c',
            'icon': 'bi-lightbulb'
        },
        {
            'name': 'Plan',
            'description': 'Create structured frameworks for research management',
            'maldreth_description': 'To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis.',
            'order': 2,
            'color_code': '#3498db',
            'icon': 'bi-clipboard-data'
        },
        {
            'name': 'Fund',
            'description': 'Acquire financial resources for research',
            'maldreth_description': 'To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.',
            'order': 3,
            'color_code': '#f39c12',
            'icon': 'bi-currency-dollar'
        },
        {
            'name': 'Collect',
            'description': 'Gather reliable, high-quality data',
            'maldreth_description': 'To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.',
            'order': 4,
            'color_code': '#27ae60',
            'icon': 'bi-collection'
        },
        {
            'name': 'Process',
            'description': 'Prepare data for analysis',
            'maldreth_description': 'To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.',
            'order': 5,
            'color_code': '#9b59b6',
            'icon': 'bi-gear'
        },
        {
            'name': 'Analyse',
            'description': 'Derive insights from processed data',
            'maldreth_description': 'To derive insights, knowledge, and understanding from processed data. Data analysis involves iterative exploration and interpretation of experimental or computational results.',
            'order': 6,
            'color_code': '#e67e22',
            'icon': 'bi-graph-up'
        },
        {
            'name': 'Store',
            'description': 'Securely record data',
            'maldreth_description': 'To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.',
            'order': 7,
            'color_code': '#34495e',
            'icon': 'bi-server'
        },
        {
            'name': 'Publish',
            'description': 'Release research data for others',
            'maldreth_description': 'To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.',
            'order': 8,
            'color_code': '#1abc9c',
            'icon': 'bi-journal-text'
        },
        {
            'name': 'Preserve',
            'description': 'Ensure long-term data accessibility',
            'maldreth_description': 'To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.',
            'order': 9,
            'color_code': '#8e44ad',
            'icon': 'bi-shield-check'
        },
        {
            'name': 'Share',
            'description': 'Make data available to humans and machines',
            'maldreth_description': 'To make data available and accessible to humans and/or machines. Data may be shared with project collaborators or published to share it with the wider research community.',
            'order': 10,
            'color_code': '#2ecc71',
            'icon': 'bi-share'
        },
        {
            'name': 'Access',
            'description': 'Control and manage data access',
            'maldreth_description': 'To control and manage data access by designated users and reusers. This may be in the form of publicly available published information.',
            'order': 11,
            'color_code': '#f1c40f',
            'icon': 'bi-key'
        },
        {
            'name': 'Transform',
            'description': 'Create new data from original sources',
            'maldreth_description': 'To create new data from the original, for example: (i) by migration into a different format; (ii) by creating a subset, by selection or query, to create newly derived results.',
            'order': 12,
            'color_code': '#e74c3c',
            'icon': 'bi-arrow-repeat'
        }
    ]
    
    # Create stages
    for stage_data in stages_data:
        existing = LifecycleStage.query.filter_by(name=stage_data['name']).first()
        if not existing:
            stage = LifecycleStage(**stage_data)
            db.session.add(stage)
    
    db.session.commit()
    
    # Create standard stage connections
    stages = {stage.name: stage for stage in LifecycleStage.query.all()}
    
    connections_data = [
        ('Conceptualise', 'Plan', 'normal'),
        ('Plan', 'Fund', 'normal'),
        ('Fund', 'Collect', 'normal'),
        ('Collect', 'Process', 'normal'),
        ('Process', 'Analyse', 'normal'),
        ('Analyse', 'Store', 'normal'),
        ('Store', 'Publish', 'normal'),
        ('Publish', 'Preserve', 'normal'),
        ('Preserve', 'Share', 'normal'),
        ('Share', 'Access', 'normal'),
        ('Access', 'Transform', 'normal'),
        ('Transform', 'Conceptualise', 'feedback'),
        # Alternative paths
        ('Process', 'Collect', 'feedback'),
        ('Analyse', 'Process', 'feedback'),
        ('Store', 'Analyse', 'alternative'),
    ]
    
    for from_name, to_name, conn_type in connections_data:
        if from_name in stages and to_name in stages:
            existing = StageConnection.query.filter_by(
                from_stage_id=stages[from_name].id,
                to_stage_id=stages[to_name].id
            ).first()
            
            if not existing:
                connection = StageConnection(
                    from_stage_id=stages[from_name].id,
                    to_stage_id=stages[to_name].id,
                    connection_type=conn_type
                )
                db.session.add(connection)
    
    db.session.commit()
    print("MaLDReTH lifecycle stages and connections initialized successfully!")
