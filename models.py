"""
models_unified.py
Unified database models for the MaLDReTH Tool Interaction Capture System.

This module defines all SQLAlchemy models for the application, including:
- Research Data Lifecycle (RDL) stages and tools
- Tool interactions and relationships
- User feedback and analytics
- System connections and metadata

The models align with the MaLDReTH 1.0 final outputs and support both
the original application functionality and the streamlined interaction capture.

For LLM/Copilot Understanding:
- MaldrethStage: Represents the 12 harmonized RDL stages
- ExemplarTool: Individual tools within each stage/category
- ToolInteraction: Detailed interaction data between tools
- ToolCategory: Groupings of related tools within stages
- UserInteraction: User feedback and engagement data
- SiteInteraction: Analytics and usage tracking
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from extensions import db


class MaldrethStage(db.Model):
    """
    Model representing the 12 stages in the MaLDReTH Research Data Lifecycle.
    
    This model stores the harmonized RDL stages as defined in the MaLDReTH 1.0
    final outputs. Each stage represents a key phase in research data management.
    
    For LLM/Copilot: This is the core organizational structure - stages like
    CONCEPTUALISE, PLAN, FUND, COLLECT, PROCESS, ANALYSE, STORE, PUBLISH, 
    PRESERVE, SHARE, ACCESS, TRANSFORM form the lifecycle framework.
    
    Attributes:
        id (int): Primary key identifier
        name (str): Stage name (e.g., 'CONCEPTUALISE', 'PLAN')
        description (str): Detailed description of the stage purpose
        position (int): Order position in the lifecycle (0-11)
        color (str): Hex color code for UI visualization
        tool_categories (relationship): Related tool categories within this stage
        tools (relationship): All exemplar tools associated with this stage
    """
    __tablename__ = 'maldreth_stages'
    
    # Primary identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # Core stage information
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, default=0)  # Order in RDL cycle (0-11)
    
    # UI/visualization properties
    color = db.Column(db.String(7), default='#007bff')  # Hex color for stage visualization
    
    # Relationships - Enable navigation between stages and their components
    # For LLM/Copilot: Use these to find all categories/tools in a stage
    tool_categories = db.relationship(
        'ToolCategory',
        backref='stage',
        lazy='dynamic',
        cascade='all, delete-orphan'  # Delete categories when stage is deleted
    )
    tools = db.relationship(
        'ExemplarTool',
        backref='stage',
        lazy='dynamic',
        cascade='all, delete-orphan'  # Delete tools when stage is deleted
    )
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return f'<MaldrethStage {self.name} (pos: {self.position})>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert stage to dictionary for JSON serialization.
        
        For LLM/Copilot: Use this method to convert stage data for API responses,
        frontend consumption, or data export. Includes all UI-relevant properties.
        
        Returns:
            Dict containing stage data with keys: id, name, description, position, color
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'position': self.position,
            'color': self.color
        }
    
    def get_tool_count(self) -> int:
        """
        Get the number of exemplar tools in this stage.
        
        For LLM/Copilot: Use this to display stage statistics or validate completeness.
        
        Returns:
            int: Count of associated exemplar tools
        """
        return self.tools.count()
    
    def get_category_count(self) -> int:
        """
        Get the number of tool categories in this stage.
        
        For LLM/Copilot: Use this to understand stage complexity/organization.
        
        Returns:
            int: Count of associated tool categories
        """
        return self.tool_categories.count()


class ToolCategory(db.Model):
    """
    Model representing categories of tools within each MaLDReTH stage.
    
    Tool categories group related tools within a stage. For example, within the
    CONCEPTUALISE stage, categories might include "Mind mapping" or "Diagramming".
    This provides a hierarchical organization: Stage > Category > Tool.
    
    For LLM/Copilot: Categories help organize tools logically. When looking for
    tools of a specific type (e.g., "Data Repository" tools), filter by category
    name across stages to find all relevant tools.
    
    Attributes:
        id (int): Primary key identifier
        name (str): Category name (e.g., "Data Repository", "Mind mapping")
        description (str): Detailed explanation of the category purpose
        stage_id (int): Foreign key linking to the parent MaLDReTH stage
        tools (relationship): All exemplar tools within this category
    """
    __tablename__ = 'tool_categories'
    
    # Primary identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # Core category information
    name = db.Column(db.String(200), nullable=False)  # Category name
    description = db.Column(db.Text)  # Detailed purpose/scope description
    
    # Relationship to parent stage
    stage_id = db.Column(
        db.Integer,
        db.ForeignKey('maldreth_stages.id'),  # Link to MaldrethStage table
        nullable=False
    )
    
    # Relationships - Enable navigation to tools within this category
    # For LLM/Copilot: Use to find all tools of a specific type/category
    tools = db.relationship(
        'ExemplarTool',
        backref='category',
        lazy='dynamic',
        cascade='all, delete-orphan'  # Delete tools when category is deleted
    )
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return f'<ToolCategory {self.name} (stage: {self.stage.name if self.stage else "None"})>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert category to dictionary for JSON serialization.
        
        For LLM/Copilot: Use this for API responses and data export.
        
        Returns:
            Dict containing category data with stage information
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stage_id': self.stage_id,
            'stage_name': self.stage.name if self.stage else None,
            'tool_count': self.tools.count()
        }


class ExemplarTool(db.Model):
    """
    Model representing individual exemplar tools within the MaLDReTH framework.
    
    Exemplar tools are specific software, platforms, or services that researchers
    use within each stage of the research data lifecycle. These represent real-world
    tools like "Jupyter", "Figshare", "SPSS", etc.
    
    For LLM/Copilot: These are the actual tools that researchers interact with.
    When building tool interactions or workflows, these are the source/target
    entities. Each tool belongs to both a stage and a category for organization.
    
    Attributes:
        id (int): Primary key identifier
        name (str): Tool name (e.g., "Jupyter", "Figshare", "SPSS")
        description (str): Tool description and capabilities
        url (str): Official tool website or documentation URL
        category_id (int): Foreign key to the tool category
        stage_id (int): Foreign key to the MaLDReTH stage
        is_active (bool): Whether the tool is currently active/supported
        source_interactions (relationship): Interactions where this tool is the source
        target_interactions (relationship): Interactions where this tool is the target
    """
    __tablename__ = 'exemplar_tools'
    
    # Primary identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # Core tool information
    name = db.Column(db.String(100), nullable=False)  # Tool name (e.g., "Jupyter")
    description = db.Column(db.Text)  # Tool capabilities and description
    url = db.Column(db.String(500))  # Official website or documentation URL
    
    # Organizational relationships
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('tool_categories.id'),  # Link to ToolCategory table
        nullable=True  # Some tools may not have specific categories
    )
    stage_id = db.Column(
        db.Integer,
        db.ForeignKey('maldreth_stages.id'),  # Link to MaldrethStage table
        nullable=False
    )
    
    # Tool status and metadata
    is_active = db.Column(db.Boolean, default=True)  # Whether tool is currently supported/available
    
    # Relationships for tool interactions
    # For LLM/Copilot: These enable finding all interactions involving this tool
    source_interactions = db.relationship(
        'ToolInteraction',
        foreign_keys='ToolInteraction.source_tool_id',  # This tool as interaction source
        backref='source_tool',
        lazy='dynamic'
    )
    target_interactions = db.relationship(
        'ToolInteraction', 
        foreign_keys='ToolInteraction.target_tool_id',  # This tool as interaction target
        backref='target_tool',
        lazy='dynamic'
    )
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return f'<ExemplarTool {self.name} (stage: {self.stage.name if self.stage else "None"})>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tool to dictionary for JSON serialization.
        
        For LLM/Copilot: Use this for API responses, data export, and frontend display.
        Includes hierarchical information (stage and category) for context.
        
        Returns:
            Dict containing complete tool information including relationships
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'category_id': self.category_id,
            'category': self.category.name if self.category else None,
            'stage_id': self.stage_id,
            'stage': self.stage.name if self.stage else None,
            'is_active': self.is_active,
            'interaction_count': self.get_interaction_count()
        }
    
    def get_interaction_count(self) -> int:
        """
        Get total number of interactions (as source or target) for this tool.
        
        For LLM/Copilot: Use this to identify the most connected/important tools
        in the ecosystem and understand tool integration patterns.
        
        Returns:
            int: Total count of interactions involving this tool
        """
        return self.source_interactions.count() + self.target_interactions.count()
    
    def get_connected_tools(self) -> List['ExemplarTool']:
        """
        Get all tools that this tool interacts with (directly connected).
        
        For LLM/Copilot: Use this to build tool relationship networks and
        suggest related tools to users.
        
        Returns:
            List of ExemplarTool objects that have interactions with this tool
        """
        connected_tools = set()
        
        # Add tools this tool connects to (as source)
        for interaction in self.source_interactions:
            connected_tools.add(interaction.target_tool)
            
        # Add tools that connect to this tool (as target)
        for interaction in self.target_interactions:
            connected_tools.add(interaction.source_tool)
            
        return list(connected_tools)


class ToolInteraction(db.Model):
    """
    Model representing detailed interactions between exemplar tools.
    
    This is the core model for capturing tool integration patterns and workflows.
    Each interaction represents a real-world connection between two tools, including
    technical details, benefits, challenges, and implementation guidance.
    
    Aligned with the Google Sheet fields from MaLDReTH 1.0 outputs for comprehensive
    interaction capture and community knowledge sharing.
    
    For LLM/Copilot: This model contains the detailed workflow information.
    Use it to understand HOW tools connect, not just THAT they connect.
    Essential for building automation, suggesting workflows, and troubleshooting.
    
    Attributes:
        id (int): Primary key identifier
        source_tool_id (int): Tool initiating the interaction
        target_tool_id (int): Tool receiving/processing from source
        interaction_type (str): Type of interaction (data_flow, integration, etc.)
        lifecycle_stage (str): RDL stage where this interaction typically occurs
        description (str): Detailed description of the interaction
        technical_details (str): Implementation specifics and requirements
        benefits (str): Advantages of this tool interaction
        challenges (str): Known issues or limitations
        examples (str): Real-world usage examples
        contact_person (str): Subject matter expert contact
        organization (str): Contributing organization
        email (str): Contact email for follow-up
        priority (str): Implementation priority (high, medium, low)
        complexity (str): Technical complexity level
        status (str): Current status (active, deprecated, experimental)
        submitted_by (str): Person who contributed this interaction data
        submitted_at (datetime): When the interaction was recorded
    """
    __tablename__ = 'tool_interactions'
    
    # Primary identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # Core interaction relationship
    # For LLM/Copilot: source_tool initiates or provides data, target_tool receives/processes
    source_tool_id = db.Column(db.Integer, db.ForeignKey('exemplar_tools.id'), nullable=False)
    target_tool_id = db.Column(db.Integer, db.ForeignKey('exemplar_tools.id'), nullable=False)
    
    # Interaction classification
    interaction_type = db.Column(db.String(100), nullable=False)  # e.g., "data_export", "API_integration"
    lifecycle_stage = db.Column(db.String(50), nullable=False)    # Which RDL stage this occurs in
    
    # Detailed interaction information
    description = db.Column(db.Text, nullable=False)      # What happens in this interaction
    technical_details = db.Column(db.Text)                # HOW to implement (APIs, formats, etc.)
    benefits = db.Column(db.Text)                         # Why use this interaction
    challenges = db.Column(db.Text)                       # Potential problems or limitations
    examples = db.Column(db.Text)                         # Real-world usage examples
    
    # Contact and attribution information
    contact_person = db.Column(db.String(100))            # Subject matter expert
    organization = db.Column(db.String(100))              # Contributing organization
    email = db.Column(db.String(100))                     # Contact for questions
    
    # Classification and status metadata
    priority = db.Column(db.String(20))                   # Implementation priority level
    complexity = db.Column(db.String(20))                 # Technical complexity assessment
    status = db.Column(db.String(20))                     # Current interaction status
    
    # Submission tracking
    submitted_by = db.Column(db.String(100))              # Data contributor
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)  # Contribution timestamp
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        source_name = self.source_tool.name if self.source_tool else "Unknown"
        target_name = self.target_tool.name if self.target_tool else "Unknown"
        return f'<ToolInteraction {source_name} -> {target_name} ({self.interaction_type})>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert interaction to dictionary for JSON serialization.
        
        For LLM/Copilot: Use this for API responses, data export, and frontend display.
        Includes complete tool information and metadata for comprehensive understanding.
        
        Returns:
            Dict containing complete interaction data with tool details
        """
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
    
    def is_bidirectional_with(self, other_interaction: 'ToolInteraction') -> bool:
        """
        Check if this interaction forms a bidirectional pair with another.
        
        For LLM/Copilot: Use this to identify two-way tool integrations
        and avoid duplicate interaction records.
        
        Args:
            other_interaction: Another ToolInteraction to compare
            
        Returns:
            bool: True if interactions are bidirectional (A->B and B->A)
        """
        return (
            self.source_tool_id == other_interaction.target_tool_id and
            self.target_tool_id == other_interaction.source_tool_id
        )


class Connection(db.Model):
    """
    Model representing directional connections between MaLDReTH lifecycle stages.
    
    These connections define the flow and relationships in the research data lifecycle.
    Used primarily for visualization and understanding stage dependencies.
    
    For LLM/Copilot: These define the "official" flow paths between stages.
    While researchers may jump between stages, these connections show the
    typical/recommended progressions in the RDL cycle.
    
    Attributes:
        id (int): Primary key identifier
        from_stage_id (int): Source MaLDReTH stage ID
        to_stage_id (int): Target MaLDReTH stage ID  
        connection_type (str): Visual style (solid, dashed) for UI rendering
    """
    __tablename__ = 'connections'
    
    # Primary identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # Stage relationship definition
    from_stage_id = db.Column(
        db.Integer,
        db.ForeignKey('maldreth_stages.id'),  # Link to MaldrethStage table
        nullable=False
    )
    to_stage_id = db.Column(
        db.Integer,
        db.ForeignKey('maldreth_stages.id'),  # Link to MaldrethStage table
        nullable=False
    )
    
    # Visual and semantic properties
    connection_type = db.Column(
        db.String(50),
        default='solid'  # UI rendering style (solid, dashed, dotted)
    )
    
    # Relationships for accessing connected stages
    # For LLM/Copilot: Use these to navigate stage dependencies and build flow diagrams
    from_stage = db.relationship(
        'MaldrethStage',
        foreign_keys=[from_stage_id],
        backref='outgoing_connections'  # All connections FROM this stage
    )
    to_stage = db.relationship(
        'MaldrethStage', 
        foreign_keys=[to_stage_id],
        backref='incoming_connections'  # All connections TO this stage
    )
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        from_name = self.from_stage.name if self.from_stage else f"Stage#{self.from_stage_id}"
        to_name = self.to_stage.name if self.to_stage else f"Stage#{self.to_stage_id}"
        return f'<Connection {from_name} -> {to_name} ({self.connection_type})>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert connection to dictionary for JSON serialization.
        
        For LLM/Copilot: Use this for building flow diagrams and stage navigation.
        
        Returns:
            Dict containing connection data with stage names
        """
        return {
            'id': self.id,
            'from_stage_id': self.from_stage_id,
            'from_stage_name': self.from_stage.name if self.from_stage else None,
            'to_stage_id': self.to_stage_id,
            'to_stage_name': self.to_stage.name if self.to_stage else None,
            'connection_type': self.connection_type
        }


class SiteInteraction(db.Model):
    """
    Model for tracking site usage analytics and user behavior patterns.
    
    Captures anonymous usage data to understand how users navigate the application
    and which features are most valuable. Useful for improving UX and identifying
    popular tools/stages.
    
    For LLM/Copilot: Use this data to understand user engagement patterns,
    identify the most accessed tools/stages, and optimize the application based
    on actual usage rather than assumptions.
    
    Attributes:
        id (int): Primary key identifier
        page_viewed (str): URL/route of the page accessed
        timestamp (datetime): When the interaction occurred (UTC)
        session_id (str): Anonymous session identifier for user journey tracking
        user_agent (str): Browser/client information for compatibility analysis
    """
    __tablename__ = 'site_interactions'
    
    # Primary identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # Interaction tracking data
    page_viewed = db.Column(db.String(200))                           # URL/route accessed
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)       # When accessed (UTC)
    session_id = db.Column(db.String(100))                           # Anonymous session ID
    user_agent = db.Column(db.String(500))                           # Browser/client info
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return f'<SiteInteraction {self.page_viewed} at {self.timestamp}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert site interaction to dictionary for analytics reporting.
        
        For LLM/Copilot: Use this for generating usage reports and analytics dashboards.
        
        Returns:
            Dict containing interaction data (excludes sensitive user_agent)
        """
        return {
            'id': self.id,
            'page_viewed': self.page_viewed,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id
            # Note: user_agent excluded for privacy
        }


class UserInteraction(db.Model):
    """
    Model for storing user feedback, questions, and community contributions.
    
    Captures structured feedback from the research community to improve the tool
    catalog, identify missing interactions, and gather real-world usage insights.
    Essential for community-driven enhancement of the MaLDReTH ecosystem.
    
    For LLM/Copilot: This model contains valuable community knowledge.
    Use feedback text to identify:
    - Missing tools or interactions
    - Common problems or use cases
    - Improvement suggestions
    - Expert contacts for specific tools/domains
    
    Attributes:
        id (int): Primary key identifier
        name (str): User's name (for attribution and follow-up)
        email (str): Contact email (for clarification and updates)
        organization (str): User's institution/company (for context)
        role (str): User's role/expertise area (researcher, IT, etc.)
        feedback (str): Structured feedback or contribution text
        submitted_at (datetime): When the feedback was submitted (UTC)
    """
    __tablename__ = 'user_interactions'
    
    # Primary identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # User identification and contact information
    name = db.Column(db.String(100), nullable=False)          # User's full name
    email = db.Column(db.String(100), nullable=False)         # Contact email
    organization = db.Column(db.String(200))                  # Institution/company
    role = db.Column(db.String(100))                          # Job title/role
    
    # Feedback content and metadata
    feedback = db.Column(db.Text)                             # User's feedback/contribution
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)  # Submission timestamp (UTC)
    
    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return f'<UserInteraction {self.email} ({self.organization}) at {self.submitted_at}>'
    
    def to_dict(self, include_contact: bool = True) -> Dict[str, Any]:
        """
        Convert user interaction to dictionary for various use cases.
        
        For LLM/Copilot: Use this for displaying feedback, generating reports,
        or exporting community contributions. Control contact info inclusion
        based on privacy requirements.
        
        Args:
            include_contact: Whether to include email and personal details
            
        Returns:
            Dict containing user interaction data
        """
        data = {
            'id': self.id,
            'feedback': self.feedback,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
        
        if include_contact:
            data.update({
                'name': self.name,
                'email': self.email,
                'organization': self.organization,
                'role': self.role
            })
        else:
            # Anonymous version for public display
            data.update({
                'organization': self.organization,  # Keep org for context
                'role': self.role  # Keep role for expertise context
            })
            
        return data
    
    def get_expertise_keywords(self) -> List[str]:
        """
        Extract potential expertise keywords from role and organization.
        
        For LLM/Copilot: Use this to categorize feedback by domain expertise
        and identify subject matter experts for specific tools or stages.
        
        Returns:
            List of keywords indicating user's potential expertise areas
        """
        keywords = []
        
        # Extract from role
        if self.role:
            role_lower = self.role.lower()
            if 'data' in role_lower:
                keywords.append('data_science')
            if 'research' in role_lower:
                keywords.append('research')
            if 'it' in role_lower or 'tech' in role_lower:
                keywords.append('technical')
            if 'library' in role_lower:
                keywords.append('information_management')
                
        # Extract from organization
        if self.organization:
            org_lower = self.organization.lower()
            if 'university' in org_lower or 'college' in org_lower:
                keywords.append('academic')
            if 'hospital' in org_lower or 'medical' in org_lower:
                keywords.append('medical')
                
        return keywords


# Database utility functions for common queries
# For LLM/Copilot: These functions provide optimized database access patterns

def get_stage_by_name(stage_name: str) -> Optional[MaldrethStage]:
    """
    Retrieve a MaLDReTH stage by its name.
    
    For LLM/Copilot: Use this when you have a stage name (e.g., from user input)
    and need the full stage object with relationships.
    
    Args:
        stage_name: Name of the stage (case-sensitive)
        
    Returns:
        MaldrethStage object or None if not found
    """
    return MaldrethStage.query.filter_by(name=stage_name).first()


def get_tools_by_stage(stage_name: str) -> List[ExemplarTool]:
    """
    Get all exemplar tools for a specific stage.
    
    For LLM/Copilot: Use this to display all tools available in a stage
    or to find tool options for building workflows.
    
    Args:
        stage_name: Name of the MaLDReTH stage
        
    Returns:
        List of ExemplarTool objects for the stage
    """
    stage = get_stage_by_name(stage_name)
    if stage:
        return stage.tools.filter_by(is_active=True).all()
    return []


def get_tool_interactions(tool_id: int, as_source: bool = True, as_target: bool = True) -> List[ToolInteraction]:
    """
    Get all interactions involving a specific tool.
    
    For LLM/Copilot: Use this to understand how a tool connects to others,
    find integration patterns, or suggest related tools.
    
    Args:
        tool_id: ID of the exemplar tool
        as_source: Include interactions where this tool is the source
        as_target: Include interactions where this tool is the target
        
    Returns:
        List of ToolInteraction objects involving the tool
    """
    interactions = []
    
    if as_source:
        interactions.extend(
            ToolInteraction.query.filter_by(source_tool_id=tool_id).all()
        )
    
    if as_target:
        interactions.extend(
            ToolInteraction.query.filter_by(target_tool_id=tool_id).all()
        )
    
    return interactions


def get_interactions_by_stage(stage_name: str) -> List[ToolInteraction]:
    """
    Get all tool interactions that occur within or involve a specific stage.
    
    For LLM/Copilot: Use this to understand the integration patterns
    typical of a particular research phase.
    
    Args:
        stage_name: Name of the MaLDReTH stage
        
    Returns:
        List of ToolInteraction objects related to the stage
    """
    # Get interactions by lifecycle stage or tool stage membership
    return ToolInteraction.query.filter(
        db.or_(
            ToolInteraction.lifecycle_stage == stage_name,
            ToolInteraction.source_tool.has(stage=get_stage_by_name(stage_name)),
            ToolInteraction.target_tool.has(stage=get_stage_by_name(stage_name))
        )
    ).all()


def get_popular_tools(limit: int = 10) -> List[tuple]:
    """
    Get the most connected tools in the ecosystem.
    
    For LLM/Copilot: Use this to identify central/important tools,
    suggest commonly used tools, or understand the ecosystem structure.
    
    Args:
        limit: Maximum number of tools to return
        
    Returns:
        List of tuples: (ExemplarTool, interaction_count)
    """
    from sqlalchemy import func
    
    # Count interactions as both source and target
    source_counts = db.session.query(
        ToolInteraction.source_tool_id,
        func.count(ToolInteraction.id).label('count')
    ).group_by(ToolInteraction.source_tool_id).subquery()
    
    target_counts = db.session.query(
        ToolInteraction.target_tool_id,
        func.count(ToolInteraction.id).label('count')
    ).group_by(ToolInteraction.target_tool_id).subquery()
    
    # Combine counts and get top tools
    popular_tools = db.session.query(
        ExemplarTool,
        (func.coalesce(source_counts.c.count, 0) + func.coalesce(target_counts.c.count, 0)).label('total_interactions')
    ).outerjoin(
        source_counts, ExemplarTool.id == source_counts.c.source_tool_id
    ).outerjoin(
        target_counts, ExemplarTool.id == target_counts.c.target_tool_id
    ).order_by(
        db.desc('total_interactions')
    ).limit(limit).all()
    
    return [(tool, count) for tool, count in popular_tools]