"""
Flask-WTF Forms for MaLDReTH Infrastructure Interactions application.

This module defines all the web forms used in the Flask application,
including validation rules and field definitions for data collection.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, EmailField,
    SubmitField, HiddenField
)
from wtforms.validators import (
    DataRequired, Length, Email, Optional, ValidationError
)


class InteractionForm(FlaskForm):
    """
    Form for creating and editing infrastructure interactions.
    
    This form collects comprehensive information about interactions between
    different infrastructure components in the research data lifecycle.
    """
    
    # Core Information
    interaction_type = SelectField(
        'Interaction Type',
        choices=[
            ('', 'Select interaction type...'),
            ('data_flow', 'Data Flow'),
            ('metadata_exchange', 'Metadata Exchange'),
            ('authentication', 'Authentication/Authorization'),
            ('workflow_integration', 'Workflow Integration'),
            ('api_integration', 'API Integration'),
            ('service_composition', 'Service Composition'),
            ('notification', 'Notification/Alerting'),
            ('monitoring', 'Monitoring/Logging'),
            ('backup_replication', 'Backup/Replication'),
            ('synchronization', 'Data Synchronization'),
            ('transformation', 'Data Transformation'),
            ('validation', 'Data Validation'),
            ('aggregation', 'Data Aggregation'),
            ('federation', 'Identity Federation'),
            ('other', 'Other')
        ],
        validators=[DataRequired(message="Please select an interaction type.")],
        description="Type of interaction between infrastructure components"
    )
    
    source_infrastructure = StringField(
        'Source Infrastructure',
        validators=[
            DataRequired(message="Source infrastructure is required."),
            Length(min=2, max=200, message="Source infrastructure must be between 2 and 200 characters.")
        ],
        description="Infrastructure component that initiates the interaction",
        render_kw={"placeholder": "e.g., Research Repository, CRIS System, Laboratory LIMS"}
    )
    
    target_infrastructure = StringField(
        'Target Infrastructure',
        validators=[
            DataRequired(message="Target infrastructure is required."),
            Length(min=2, max=200, message="Target infrastructure must be between 2 and 200 characters.")
        ],
        description="Infrastructure component that receives or responds to the interaction",
        render_kw={"placeholder": "e.g., Data Analysis Platform, Preservation System, Publication Portal"}
    )
    
    lifecycle_stage = SelectField(
        'Research Data Lifecycle Stage',
        choices=[
            ('', 'Select lifecycle stage...'),
            ('conceptualise', 'Conceptualise'),
            ('plan', 'Plan'),
            ('fund', 'Fund'),
            ('collect', 'Collect'),
            ('process', 'Process'),
            ('analyse', 'Analyse'),
            ('store', 'Store'),
            ('publish', 'Publish'),
            ('preserve', 'Preserve'),
            ('share', 'Share'),
            ('access', 'Access'),
            ('transform', 'Transform'),
            ('multiple', 'Multiple Stages'),
            ('cross_cutting', 'Cross-cutting')
        ],
        validators=[DataRequired(message="Please select a lifecycle stage.")],
        description="Primary research data lifecycle stage where this interaction occurs"
    )
    
    description = TextAreaField(
        'Description',
        validators=[
            DataRequired(message="Description is required."),
            Length(min=10, max=2000, message="Description must be between 10 and 2000 characters.")
        ],
        description="Detailed description of the interaction, its purpose, and context",
        render_kw={
            "placeholder": "Describe the interaction, what it accomplishes, and why it's important...",
            "rows": 4
        }
    )
    
    # Technical Details
    technical_details = TextAreaField(
        'Technical Implementation Details',
        validators=[
            Optional(),
            Length(max=2000, message="Technical details must be less than 2000 characters.")
        ],
        description="Technical specifications, protocols, APIs, or implementation details",
        render_kw={
            "placeholder": "e.g., REST API calls, database connections, file transfers, message queues...",
            "rows": 3
        }
    )
    
    standards_protocols = StringField(
        'Standards/Protocols',
        validators=[
            Optional(),
            Length(max=200, message="Standards/protocols must be less than 200 characters.")
        ],
        description="Relevant standards, protocols, or specifications used",
        render_kw={"placeholder": "e.g., SWORD, OAI-PMH, REST, SAML, OAuth 2.0, Dublin Core"}
    )
    
    # Impact Assessment
    benefits = TextAreaField(
        'Benefits/Advantages',
        validators=[
            Optional(),
            Length(max=1000, message="Benefits must be less than 1000 characters.")
        ],
        description="Expected benefits, advantages, or positive outcomes",
        render_kw={
            "placeholder": "What benefits does this interaction provide? How does it improve the research process?",
            "rows": 3
        }
    )
    
    challenges = TextAreaField(
        'Challenges/Limitations',
        validators=[
            Optional(),
            Length(max=1000, message="Challenges must be less than 1000 characters.")
        ],
        description="Known challenges, limitations, or potential issues",
        render_kw={
            "placeholder": "What challenges exist? What are the technical or organizational barriers?",
            "rows": 3
        }
    )
    
    examples = TextAreaField(
        'Examples/Use Cases',
        validators=[
            Optional(),
            Length(max=1000, message="Examples must be less than 1000 characters.")
        ],
        description="Specific examples, use cases, or real-world implementations",
        render_kw={
            "placeholder": "Provide concrete examples or scenarios where this interaction occurs...",
            "rows": 3
        }
    )
    
    # Contact Information
    contact_person = StringField(
        'Contact Person',
        validators=[
            Optional(),
            Length(max=200, message="Contact person must be less than 200 characters.")
        ],
        description="Name of the person providing this information",
        render_kw={"placeholder": "Dr. Jane Smith"}
    )
    
    organization = StringField(
        'Organization/Institution',
        validators=[
            Optional(),
            Length(max=200, message="Organization must be less than 200 characters.")
        ],
        description="Organization or institution name",
        render_kw={"placeholder": "University of Example, Research Institute"}
    )
    
    email = EmailField(
        'Email Address',
        validators=[
            Optional(),
            Email(message="Please enter a valid email address."),
            Length(max=200, message="Email must be less than 200 characters.")
        ],
        description="Contact email address",
        render_kw={"placeholder": "jane.smith@example.edu"}
    )
    
    # Classification
    priority = SelectField(
        'Priority Level',
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='medium',
        validators=[Optional()],
        description="Priority level for implementing this interaction"
    )
    
    complexity = SelectField(
        'Implementation Complexity',
        choices=[
            ('simple', 'Simple'),
            ('moderate', 'Moderate'),
            ('complex', 'Complex'),
            ('very_complex', 'Very Complex')
        ],
        default='moderate',
        validators=[Optional()],
        description="Expected complexity of implementing this interaction"
    )
    
    status = SelectField(
        'Current Status',
        choices=[
            ('proposed', 'Proposed'),
            ('planned', 'Planned'),
            ('in_development', 'In Development'),
            ('implemented', 'Implemented'),
            ('operational', 'Operational'),
            ('deprecated', 'Deprecated')
        ],
        default='proposed',
        validators=[Optional()],
        description="Current implementation status"
    )
    
    # Additional Information
    notes = TextAreaField(
        'Additional Notes',
        validators=[
            Optional(),
            Length(max=1000, message="Notes must be less than 1000 characters.")
        ],
        description="Any additional notes, comments, or relevant information",
        render_kw={
            "placeholder": "Any other relevant information, references, or context...",
            "rows": 3
        }
    )
    
    # Form submission
    submit = SubmitField('Save Interaction')
    
    def validate_source_infrastructure(self, field):
        """Custom validation for source infrastructure."""
        if field.data and field.data.lower() == self.target_infrastructure.data.lower():
            raise ValidationError("Source and target infrastructure cannot be the same.")
    
    def validate_technical_details(self, field):
        """Custom validation for technical details."""
        if field.data:
            # Check for potentially sensitive information
            sensitive_terms = ['password', 'secret', 'key', 'token', 'credential']
            field_lower = field.data.lower()
            for term in sensitive_terms:
                if term in field_lower:
                    raise ValidationError(
                        f"Please avoid including sensitive information like '{term}' in technical details."
                    )


class SearchForm(FlaskForm):
    """
    Form for searching and filtering interactions.
    
    This form provides search and filter capabilities for the interactions list.
    """
    
    search = StringField(
        'Search',
        validators=[
            Optional(),
            Length(max=200, message="Search term must be less than 200 characters.")
        ],
        render_kw={"placeholder": "Search interactions..."}
    )
    
    interaction_type = SelectField(
        'Filter by Type',
        choices=[('', 'All Types')],  # Will be populated dynamically
        validators=[Optional()]
    )
    
    lifecycle_stage = SelectField(
        'Filter by Stage',
        choices=[('', 'All Stages')],  # Will be populated dynamically
        validators=[Optional()]
    )
    
    priority = SelectField(
        'Filter by Priority',
        choices=[
            ('', 'All Priorities'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        validators=[Optional()]
    )
    
    status = SelectField(
        'Filter by Status',
        choices=[
            ('', 'All Statuses'),
            ('proposed', 'Proposed'),
            ('planned', 'Planned'),
            ('in_development', 'In Development'),
            ('implemented', 'Implemented'),
            ('operational', 'Operational'),
            ('deprecated', 'Deprecated')
        ],
        validators=[Optional()]
    )
    
    submit = SubmitField('Search')


def help():
    """
    Display help information for the forms module.
    
    This function provides comprehensive information about the forms,
    their fields, validation rules, and usage examples.
    """
    print("""
    MaLDReTH Infrastructure Interactions - Forms Module
    ==================================================
    
    This module defines Flask-WTF forms for the web application.
    
    Forms Available:
    ----------------
    
    1. InteractionForm:
       - Used for creating and editing infrastructure interactions
       - Includes comprehensive validation rules
       - Covers all aspects of interaction data collection
       
       Fields:
       - interaction_type (Required): Type of interaction
       - source_infrastructure (Required): Source component
       - target_infrastructure (Required): Target component  
       - lifecycle_stage (Required): Research data lifecycle stage
       - description (Required): Detailed description
       - technical_details (Optional): Implementation details
       - standards_protocols (Optional): Relevant standards
       - benefits (Optional): Expected benefits
       - challenges (Optional): Known challenges
       - examples (Optional): Use cases and examples
       - contact_person (Optional): Contact information
       - organization (Optional): Institution name
       - email (Optional): Contact email
       - priority (Optional): Priority level
       - complexity (Optional): Implementation complexity
       - status (Optional): Current status
       - notes (Optional): Additional notes
    
    2. SearchForm:
       - Used for searching and filtering interactions
       - Provides various filter options
       
       Fields:
       - search: Free text search
       - interaction_type: Filter by interaction type
       - lifecycle_stage: Filter by lifecycle stage
       - priority: Filter by priority level
       - status: Filter by implementation status
    
    Validation Features:
    -------------------
    - Required field validation
    - Length validation for all text fields
    - Email format validation
    - Custom validation to prevent duplicate source/target
    - Security validation to prevent sensitive data exposure
    
    Usage Example:
    --------------
    from forms import InteractionForm
    
    form = InteractionForm()
    if form.validate_on_submit():
        # Process form data
        interaction = Interaction(
            interaction_type=form.interaction_type.data,
            source_infrastructure=form.source_infrastructure.data,
            # ... other fields
        )
    
    Security Features:
    ------------------
    - CSRF protection via Flask-WTF
    - Input sanitization and validation
    - Sensitive information detection
    - Length limits to prevent DoS attacks
    
    For more information, see the Flask-WTF documentation:
    https://flask-wtf.readthedocs.io/
    """)


if __name__ == '__main__':
    help()
