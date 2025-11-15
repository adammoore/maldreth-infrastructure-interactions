"""
streamlined_app.py
PRISM - Platform for Research Infrastructure Synergy Mapping

A comprehensive Flask application for capturing and visualizing tool interactions
across the research data lifecycle, evolved from the MaLDReTH project.

PRISM provides:
1. The 12 harmonised Research Data Lifecycle (RDL) stages.
2. A comprehensive list of tool categories and exemplar tools.
3. Advanced interaction capture with predefined types and lifecycle stages.
4. Visual indicators for open source tools and detailed interaction views.
5. CSV export capabilities and enhanced API functionality.
"""

import os
import csv
import logging
import math
from io import StringIO
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import editable glossary content
try:
    from config.glossary_content import FAQ_ITEMS, MALDRETH_TERMINOLOGY
    GLOSSARY_CONFIG_LOADED = True
except ImportError:
    # Fallback to None if config not available
    FAQ_ITEMS = None
    MALDRETH_TERMINOLOGY = None
    GLOSSARY_CONFIG_LOADED = False
    logging.warning("Glossary config not found, using hardcoded values")

# PRISM Configuration Constants
INTERACTION_TYPES = [
    'API Integration',
    'Data Exchange',
    'Metadata Exchange', 
    'File Format Conversion',
    'Workflow Integration',
    'Plugin/Extension',
    'Direct Database Connection',
    'Web Service',
    'Command Line Interface',
    'Import/Export',
    'Other'
]

LIFECYCLE_STAGES = [
    'CONCEPTUALISE',
    'PLAN',
    'FUND',
    'COLLECT',
    'PROCESS',
    'ANALYSE',
    'STORE',
    'PUBLISH',
    'PRESERVE',
    'SHARE',
    'ACCESS',
    'TRANSFORM'
]

# Interaction Type Definitions with examples and guidance
INTERACTION_TYPE_DEFINITIONS = {
    'API Integration': {
        'definition': 'Direct programmatic connection between tools using Application Programming Interfaces',
        'example': 'DMPTool connects to RSpace via REST API to sync data management plans',
        'when_to_use': 'When tools communicate programmatically with structured data exchange',
        'technical_indicators': ['REST API', 'GraphQL', 'SOAP', 'JSON', 'XML', 'OAuth'],
        'common_protocols': ['HTTP/HTTPS', 'REST', 'SOAP', 'gRPC']
    },
    'Data Exchange': {
        'definition': 'Transfer of research data files or datasets between tools',
        'example': 'Zenodo receives data files exported from GitHub repositories',
        'when_to_use': 'When the primary function is moving data content between systems',
        'technical_indicators': ['file transfer', 'bulk data', 'datasets', 'repository sync'],
        'common_protocols': ['FTP', 'SFTP', 'rsync', 'cloud storage APIs']
    },
    'Metadata Exchange': {
        'definition': 'Transfer of descriptive information about data without moving the data itself',
        'example': 'ORCID profile information linked to publications in Zenodo',
        'when_to_use': 'When exchanging descriptions, citations, or contextual information',
        'technical_indicators': ['metadata', 'schema', 'descriptive info', 'catalog'],
        'common_protocols': ['OAI-PMH', 'SWORD', 'Dublin Core', 'DataCite']
    },
    'File Format Conversion': {
        'definition': 'Transformation of data from one file format to another',
        'example': 'Converting CSV data to Parquet format for analysis',
        'when_to_use': 'When format transformation is the primary interaction purpose',
        'technical_indicators': ['format change', 'conversion', 'transformation', 'encoding'],
        'common_formats': ['CSV', 'JSON', 'XML', 'Parquet', 'HDF5', 'NetCDF']
    },
    'Workflow Integration': {
        'definition': 'Tools combined into multi-step research workflows or pipelines',
        'example': 'Jupyter Notebook packaged with Docker for reproducible analysis',
        'when_to_use': 'When tools are orchestrated together in a sequence',
        'technical_indicators': ['pipeline', 'workflow', 'orchestration', 'automation'],
        'common_tools': ['Airflow', 'Nextflow', 'Snakemake', 'Galaxy', 'Taverna']
    },
    'Plugin/Extension': {
        'definition': 'One tool extends functionality of another through add-ons or plugins',
        'example': 'Zotero plugin installed in Microsoft Word for citation management',
        'when_to_use': 'When one tool adds features directly into another tool\'s interface',
        'technical_indicators': ['plugin', 'extension', 'add-on', 'module'],
        'common_patterns': ['Browser extensions', 'IDE plugins', 'Office add-ins']
    },
    'Direct Database Connection': {
        'definition': 'Tools query or write to shared database infrastructure',
        'example': 'Analysis tool connects directly to PostgreSQL research database',
        'when_to_use': 'When tools share underlying data storage layer',
        'technical_indicators': ['database', 'SQL', 'NoSQL', 'direct connection'],
        'common_databases': ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch']
    },
    'Web Service': {
        'definition': 'Tools interact via web-based service endpoints (may include APIs)',
        'example': 'Data repository accessed via OAI-PMH harvesting protocol',
        'when_to_use': 'For web-protocol-based interactions like HTTP, SOAP, OAI-PMH',
        'technical_indicators': ['web service', 'endpoint', 'WSDL', 'service oriented'],
        'common_protocols': ['HTTP', 'SOAP', 'XML-RPC', 'OAI-PMH']
    },
    'Command Line Interface': {
        'definition': 'Tools invoked or controlled via terminal commands or scripts',
        'example': 'Python script calls FFmpeg via command line to process video data',
        'when_to_use': 'When interaction happens through shell commands or scripts',
        'technical_indicators': ['CLI', 'bash', 'shell script', 'command line'],
        'common_contexts': ['Batch processing', 'Automation scripts', 'HPC jobs']
    },
    'Import/Export': {
        'definition': 'Manual or semi-automated file-based data transfer between tools',
        'example': 'Export CSV from REDCap, import into R for analysis',
        'when_to_use': 'When users manually transfer files between systems',
        'technical_indicators': ['export', 'import', 'download', 'upload', 'manual transfer'],
        'common_formats': ['CSV', 'Excel', 'JSON', 'XML', 'text files']
    },
    'Other': {
        'definition': 'Interaction types not covered by standard categories',
        'example': 'Custom or novel integration approaches',
        'when_to_use': 'When no other category fits; please describe in Technical Details',
        'technical_indicators': ['custom', 'proprietary', 'novel', 'unique'],
        'note': 'Please provide detailed description to help us improve categorization'
    }
}

# Lifecycle Stage Definitions with detailed information
LIFECYCLE_STAGE_DEFINITIONS = {
    'CONCEPTUALISE': {
        'definition': 'To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.',
        'activities': ['Literature review', 'Hypothesis formulation', 'Research question development', 'Defining data requirements', 'Scope definition'],
        'typical_tools': ['Reference managers', 'Mind mapping tools', 'Literature databases', 'Ideation platforms'],
        'duration': 'Weeks to months',
        'outputs': ['Research questions', 'Hypotheses', 'Initial concepts', 'Data requirements'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True
    },
    'PLAN': {
        'definition': 'To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis. Data management plans (DMP) should be established for this phase of the lifecycle.',
        'activities': ['Study design', 'Protocol development', 'Resource planning', 'DMP creation', 'Defining methodologies', 'Resource identification'],
        'typical_tools': ['DMP tools', 'Project management', 'Protocol repositories', 'DMPTool', 'DMPonline'],
        'duration': 'Weeks to months',
        'outputs': ['Data Management Plans', 'Protocols', 'Study designs', 'Resource allocation plans'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True
    },
    'FUND': {
        'definition': 'To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.',
        'activities': ['Grant writing', 'Budget planning', 'Proposal submission', 'Identifying funding sources', 'Financial planning'],
        'typical_tools': ['Grant management systems', 'Budget calculators', 'Proposal tools', 'Funding databases'],
        'duration': 'Months to years',
        'outputs': ['Grant proposals', 'Budgets', 'Funding awards', 'Financial plans'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True,
        'note': 'Note: Tools identified for FUND were omitted from tool categorisation as they were not classified as digital research tools'
    },
    'COLLECT': {
        'definition': 'To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.',
        'activities': ['Experiments', 'Surveys', 'Observations', 'Measurements', 'Sampling', 'Data acquisition'],
        'typical_tools': ['Lab instruments', 'Survey platforms', 'Sensors', 'Data loggers', 'Electronic lab notebooks'],
        'duration': 'Days to years',
        'outputs': ['Raw data', 'Observations', 'Measurements', 'Samples', 'Experimental data'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True,
        'note': 'COLLECT > PROCESS > ANALYSE > STORE may be a repeating cycle'
    },
    'PROCESS': {
        'definition': 'To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data. It may also involve the creation and definition of metadata for use during analysis, such as acquiring provenance from instruments and tools used during data collection.',
        'activities': ['Data cleaning', 'Quality assurance', 'Normalization', 'Format conversion', 'Metadata creation', 'Filtering', 'Structuring'],
        'typical_tools': ['Data cleaning tools', 'ETL platforms', 'Quality control software', 'OpenRefine', 'Data wrangling tools'],
        'duration': 'Days to months',
        'outputs': ['Cleaned datasets', 'Quality reports', 'Processed data', 'Metadata', 'Analysis-ready data'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True,
        'note': 'COLLECT > PROCESS > ANALYSE > STORE may be a repeating cycle'
    },
    'ANALYSE': {
        'definition': 'To derive insights, knowledge, and understanding from processed data. Data analysis involves iterative exploration and interpretation of experimental or computational results, often utilising mathematical models and formulae to investigate relationships between experimental variables. Distinct data analysis techniques and methodologies are applied according to the data type (quantitative vs qualitative).',
        'activities': ['Statistical tests', 'Modeling', 'Visualization', 'Pattern discovery', 'Iterative exploration', 'Interpretation'],
        'typical_tools': ['R', 'Python', 'SPSS', 'MATLAB', 'Jupyter', 'Statistical software', 'Analysis platforms'],
        'duration': 'Weeks to months',
        'outputs': ['Analysis results', 'Statistical models', 'Visualizations', 'Insights', 'Interpretations'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True,
        'note': 'COLLECT > PROCESS > ANALYSE > STORE may be a repeating cycle'
    },
    'STORE': {
        'definition': 'To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.',
        'activities': ['Active storage', 'Backup', 'Version control', 'Collaboration', 'Integrity maintenance', 'Security management'],
        'typical_tools': ['Cloud storage', 'Version control', 'Lab servers', 'Collaborative platforms', 'Git', 'Institutional storage'],
        'duration': 'Duration of project',
        'outputs': ['Backed up data', 'Version history', 'Shared datasets', 'Secure storage'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True,
        'note': 'COLLECT > PROCESS > ANALYSE > STORE may be a repeating cycle'
    },
    'PUBLISH': {
        'definition': 'To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.',
        'activities': ['Paper writing', 'Peer review', 'Conference presentations', 'Preprints', 'Data publication', 'Metadata creation', 'DOI assignment'],
        'typical_tools': ['Journal systems', 'Preprint servers', 'Writing tools', 'LaTeX', 'Data journals', 'Repository platforms'],
        'duration': 'Months to years',
        'outputs': ['Publications', 'Presentations', 'Preprints', 'Published datasets', 'DOIs'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True
    },
    'PRESERVE': {
        'definition': 'To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible. Data preservation is more than data storage and backup, since data can be stored and backed up without being preserved. Preservation should include curation activities such as data cleaning, validation, assigning preservation metadata, assigning representation information, and ensuring acceptable data structures and file formats. At a minimum, data and associated metadata should be published in a trustworthy digital repository and clearly cited in the accompanying journal article unless this is not possible (e.g. due to the privacy or safety concerns).',
        'activities': ['Archiving', 'Format migration', 'Metadata enrichment', 'Curation', 'Data cleaning', 'Validation', 'Format standardization'],
        'typical_tools': ['Repositories', 'Archives', 'Preservation systems', 'Digital curation tools', 'Trustworthy repositories'],
        'duration': 'Permanent',
        'outputs': ['Archived datasets', 'DOIs', 'Preserved research outputs', 'Preservation metadata', 'Curated collections'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True
    },
    'SHARE': {
        'definition': 'To make data available and accessible to humans and/or machines. Data may be shared with project collaborators or published to share it with the wider research community and society at large. Data sharing is not limited to open data or public data, and can be done during various stages of the research data lifecycle. At a minimum, data and associated metadata should be published in a trustworthy digital repository and clearly cited in the accompanying journal article.',
        'activities': ['Publishing datasets', 'Access control', 'License assignment', 'Documentation', 'Collaboration', 'Community sharing'],
        'typical_tools': ['Data repositories', 'Institutional repositories', 'Figshare', 'Zenodo', 'Dryad', 'Sharing platforms'],
        'duration': 'Ongoing',
        'outputs': ['Shared datasets', 'Data publications', 'Access portals', 'Collaborative workspaces'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True
    },
    'ACCESS': {
        'definition': 'To control and manage data access by designated users and reusers. This may be in the form of publicly available published information. Necessary access control and authentication methods are applied.',
        'activities': ['Data discovery', 'Search', 'Download', 'API access', 'Access control', 'Authentication management'],
        'typical_tools': ['Data catalogs', 'Search engines', 'Repository interfaces', 'APIs', 'Access management systems'],
        'duration': 'Ongoing',
        'outputs': ['Downloaded data', 'Retrieved datasets', 'Access logs', 'Usage statistics'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True
    },
    'TRANSFORM': {
        'definition': 'To create new data from the original, for example: (i) by migration into a different format; (ii) by creating a subset, by selection or query, to create newly derived results, perhaps for publication; or, (iii) combining or appending with other data.',
        'activities': ['Format conversion', 'Subset creation', 'Data integration', 'Reanalysis', 'Data migration', 'Query and selection'],
        'typical_tools': ['Conversion tools', 'Query systems', 'Integration platforms', 'Analysis tools', 'Data transformation pipelines'],
        'duration': 'Varies',
        'outputs': ['Transformed data', 'Subsets', 'Integrated datasets', 'New research', 'Derived datasets'],
        'source': 'RDA MaLDReTH Deliverable 1',
        'verified': True
    }
}

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///streamlined_maldreth.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Add custom Jinja2 filters for trigonometric functions
@app.template_filter('cos')
def cos_filter(degrees):
    """Convert degrees to cosine value."""
    return math.cos(math.radians(float(degrees)))

@app.template_filter('sin')
def sin_filter(degrees):
    """Convert degrees to sine value."""
    return math.sin(math.radians(float(degrees)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_tool_name(name):
    """Normalize tool names for comparison and deduplication."""
    if not name:
        return ""
    return name.lower().strip().replace('(', '').replace(')', '').replace('.', '').replace('-', '').replace('_', '').replace(' ', '')



# --- Data Models ---

class MaldrethStage(db.Model):
    """Model representing the 12 stages in the MaLDReTH RDL."""
    __tablename__ = 'maldreth_stages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, default=0)
    color = db.Column(db.String(7), default='#007bff')
    tool_categories = db.relationship('ToolCategory', backref='stage', lazy='dynamic', cascade='all, delete-orphan')

class ToolCategory(db.Model):
    """Model representing a category of tools within a stage."""
    __tablename__ = 'tool_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage_id = db.Column(db.Integer, db.ForeignKey('maldreth_stages.id'), nullable=False)
    tools = db.relationship('ExemplarTool', backref='category', lazy='dynamic', cascade='all, delete-orphan')

class ExemplarTool(db.Model):
    """Model representing exemplar tools within each category."""
    __tablename__ = 'exemplar_tools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    stage_id = db.Column(db.Integer, db.ForeignKey('maldreth_stages.id'), nullable=True)  # Now nullable for CSV imports
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=True)  # Now nullable for CSV imports
    is_active = db.Column(db.Boolean, default=True)
    is_open_source = db.Column(db.Boolean, default=False)
    provider = db.Column(db.String(200))  # MaLDReTH compatibility: tool provider/organization

    # New fields for enriched metadata
    license = db.Column(db.String(100))  # License type (MIT, Apache, GPL, etc.)
    github_url = db.Column(db.String(500))  # GitHub repository URL
    notes = db.Column(db.Text)  # Additional notes and context
    created_via = db.Column(db.String(100), default='UI')  # 'UI', 'CSV Import', 'Discovery System'
    is_archived = db.Column(db.Boolean, default=False)  # Soft delete flag

    # Existing fields
    auto_created = db.Column(db.Boolean, default=False)  # Track if created from CSV import
    import_source = db.Column(db.String(100))  # Track origin of tool data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stage = db.relationship('MaldrethStage', foreign_keys=[stage_id], backref='tools')
    source_interactions = db.relationship('ToolInteraction', foreign_keys='ToolInteraction.source_tool_id', backref='source_tool', lazy='dynamic')
    target_interactions = db.relationship('ToolInteraction', foreign_keys='ToolInteraction.target_tool_id', backref='target_tool', lazy='dynamic')

class ToolInteraction(db.Model):
    """Model representing interactions between tools, aligned with the Google Sheet fields."""
    __tablename__ = 'tool_interactions'
    id = db.Column(db.Integer, primary_key=True)
    source_tool_id = db.Column(db.Integer, db.ForeignKey('exemplar_tools.id'), nullable=False)
    target_tool_id = db.Column(db.Integer, db.ForeignKey('exemplar_tools.id'), nullable=False)
    interaction_type = db.Column(db.String(100), nullable=False)

    # DEPRECATED: lifecycle_stage is now auto-computed from source/target tools
    # Kept for backward compatibility during migration, but no longer user-facing
    lifecycle_stage = db.Column(db.String(50), nullable=True)  # Made nullable for migration

    description = db.Column(db.Text, nullable=False)
    technical_details = db.Column(db.Text)
    benefits = db.Column(db.Text)
    challenges = db.Column(db.Text)
    examples = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    organization = db.Column(db.String(100))
    email = db.Column(db.String(100))
    priority = db.Column(db.String(20))
    complexity = db.Column(db.String(20))
    status = db.Column(db.String(20))
    submitted_by = db.Column(db.String(100))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # New fields for curation
    auto_created = db.Column(db.Boolean, default=False)  # Track if created from CSV/Discovery
    is_archived = db.Column(db.Boolean, default=False)  # Soft delete flag

    @property
    def lifecycle_stages(self):
        """
        Return list of lifecycle stages involved in this interaction.
        Computed from source and target tools' assigned stages.

        Returns:
            list: [source_stage_name, target_stage_name]
        """
        stages = []
        if self.source_tool and self.source_tool.stage:
            stages.append(self.source_tool.stage.name)
        if self.target_tool and self.target_tool.stage:
            stages.append(self.target_tool.stage.name)
        return stages

    @property
    def lifecycle_stages_display(self):
        """
        Return formatted lifecycle stages for display.

        Returns:
            str: "STAGE1" if same stage, "STAGE1 → STAGE2" if different
        """
        stages = self.lifecycle_stages
        if not stages:
            return "Unknown"
        if len(stages) == 1:
            return stages[0]
        if len(set(stages)) == 1:  # Both same stage
            return stages[0]
        return f"{stages[0]} → {stages[1]}"

class Feedback(db.Model):
    """Model for collecting user feedback on PRISM alpha."""
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))  # Usability, Data Quality, Features, Documentation, Other
    feedback_text = db.Column(db.Text, nullable=False)
    page_url = db.Column(db.String(500))  # Page where feedback originated
    contact_name = db.Column(db.String(200))  # Optional
    contact_email = db.Column(db.String(200))  # Optional
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # new, reviewed, addressed
    user_agent = db.Column(db.String(500))  # Browser/device info


# --- Helper Functions ---

def find_or_create_tool_from_csv(tool_name, import_source='CSV Import'):
    """Find existing tool by normalized name or create new one with deduplication."""
    try:
        # Normalize the tool name for comparison
        normalized_name = normalize_tool_name(tool_name)
        
        # Look for existing tools with similar normalized names
        existing_tools = ExemplarTool.query.filter(
            func.lower(func.replace(func.replace(func.replace(ExemplarTool.name, ' ', ''), '-', ''), '.', '')) == normalized_name
        ).all()
        
        if existing_tools:
            # Return the first canonical tool
            canonical_tool = existing_tools[0]
            logger.info(f"Found existing tool for CSV import: {canonical_tool.name} (ID: {canonical_tool.id}) instead of creating '{tool_name}'")
            return canonical_tool, False  # Found existing
        
        # No existing tool found, create new one
        # Get a default category for unknown tools (use first available category)
        default_category = ToolCategory.query.first()
        if not default_category:
            # If no categories exist, create a default one
            default_stage = MaldrethStage.query.first()
            if not default_stage:
                raise Exception("No stages exist in database - cannot create tools")
            
            default_category = ToolCategory(
                name="Imported Tools",
                description="Auto-created category for tools imported from CSV",
                stage_id=default_stage.id
            )
            db.session.add(default_category)
            db.session.flush()  # Get the ID
        
        # Create the new tool with safe field handling
        tool_data = {
            'name': tool_name,
            'description': f"Auto-created from {import_source}: {tool_name}",
            'stage_id': default_category.stage_id,
            'category_id': default_category.id,
            'is_active': True
        }
        
        # Add new fields only if they exist in the schema
        try:
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('exemplar_tools')]
            
            if 'auto_created' in columns:
                tool_data['auto_created'] = True
            if 'import_source' in columns:
                tool_data['import_source'] = import_source
            if 'provider' in columns:
                tool_data['provider'] = "Unknown"
                
        except Exception as e:
            logger.warning(f"Could not check schema for new fields: {e}")
        
        new_tool = ExemplarTool(**tool_data)
        
        db.session.add(new_tool)
        db.session.flush()  # Get the ID without committing
        
        logger.info(f"Auto-created new tool from CSV: {tool_name} (ID: {new_tool.id})")
        return new_tool, True  # Created new
        
    except Exception as e:
        logger.error(f"Error finding/creating tool from CSV {tool_name}: {e}")
        raise


# --- Routes ---

@app.route('/')
def index():
    """Main page displaying MaLDReTH cycle, categories, and tools."""
    try:
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        total_interactions = ToolInteraction.query.count()
        total_tools = ExemplarTool.query.count()
        total_stages = MaldrethStage.query.count()
        
        # Get recent interactions (last 5)
        recent_interactions = ToolInteraction.query.order_by(ToolInteraction.submitted_at.desc()).limit(5).all()
        
        return render_template('streamlined_index.html',
                             stages=stages,
                             total_interactions=total_interactions,
                             total_tools=total_tools,
                             total_stages=total_stages,
                             recent_interactions=recent_interactions)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/add-interaction', methods=['GET', 'POST'])
def add_interaction():
    """
    Add a new tool interaction using the unified progressive disclosure form.

    Note: lifecycle_stage is no longer user-input; it's auto-computed from
    source and target tools (Co-chairs meeting Nov 13, 2025).
    """
    tools = ExemplarTool.query.filter_by(is_active=True).order_by(ExemplarTool.name).all()
    interaction_types = INTERACTION_TYPES

    if request.method == 'POST':
        try:
            # Validate required fields
            if not request.form.get('description'):
                flash('Description is required.', 'danger')
                return redirect(url_for('add_interaction'))

            interaction = ToolInteraction(
                source_tool_id=int(request.form.get('source_tool_id')),
                target_tool_id=int(request.form.get('target_tool_id')),
                interaction_type=request.form.get('interaction_type'),
                # lifecycle_stage removed - now auto-computed from tools
                description=request.form.get('description'),
                # Optional fields from collapsed sections:
                technical_details=request.form.get('technical_details'),
                benefits=request.form.get('benefits'),
                challenges=request.form.get('challenges'),
                examples=request.form.get('examples'),
                contact_person=request.form.get('contact_person'),
                organization=request.form.get('organization'),
                email=request.form.get('email'),
                priority=request.form.get('priority', 'Medium'),
                complexity=request.form.get('complexity', 'Medium'),
                status=request.form.get('status', 'Active'),
                submitted_by=request.form.get('submitted_by', 'Anonymous')
            )

            db.session.add(interaction)
            db.session.commit()

            logger.info(f"New interaction added: {interaction.interaction_type} between {interaction.source_tool.name} and {interaction.target_tool.name} (ID: {interaction.id})")

            flash('Interaction added successfully!', 'success')
            return redirect(url_for('interaction_detail', interaction_id=interaction.id))

        except ValueError as e:
            logger.error(f"Validation error adding interaction: {e}")
            db.session.rollback()
            flash('Invalid input. Please check your selections and try again.', 'danger')
            return redirect(url_for('add_interaction'))

        except Exception as e:
            logger.error(f"Error adding interaction: {e}")
            db.session.rollback()
            flash('Error adding interaction. Please try again.', 'danger')
            return redirect(url_for('add_interaction'))

    # GET request - show unified form
    return render_template('add_interaction_unified.html',
                         tools=tools,
                         interaction_types=interaction_types)

@app.route('/interactions')
def view_interactions():
    """View all interactions with search and filter support."""
    try:
        interactions = ToolInteraction.query.order_by(ToolInteraction.submitted_at.desc()).all()
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()

        return render_template('streamlined_view_interactions.html',
                             interactions=interactions,
                             interaction_types=INTERACTION_TYPES,
                             stages=stages)
    except Exception as e:
        logger.error(f"Error viewing interactions: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/interaction/<int:interaction_id>')
def interaction_detail(interaction_id):
    """View detailed information about a specific interaction."""
    try:
        interaction = ToolInteraction.query.get_or_404(interaction_id)
        return render_template('streamlined_interaction_detail.html', interaction=interaction)
    except Exception as e:
        logger.error(f"Error viewing interaction detail: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/interaction/<int:interaction_id>/edit', methods=['GET', 'POST'])
def edit_interaction(interaction_id):
    """Edit an existing interaction (curation function)."""
    try:
        interaction = ToolInteraction.query.get_or_404(interaction_id)
        
        if request.method == 'POST':
            # Update interaction with form data
            interaction.source_tool_id = request.form.get('source_tool_id')
            interaction.target_tool_id = request.form.get('target_tool_id')
            interaction.interaction_type = request.form.get('interaction_type')
            # lifecycle_stage removed - now auto-computed from tools (Co-chairs Nov 13, 2025)
            interaction.description = request.form.get('description')
            interaction.technical_details = request.form.get('technical_details')
            interaction.benefits = request.form.get('benefits')
            interaction.challenges = request.form.get('challenges')
            interaction.examples = request.form.get('examples')
            interaction.contact_person = request.form.get('contact_person')
            interaction.organization = request.form.get('organization')
            interaction.email = request.form.get('email')
            interaction.priority = request.form.get('priority')
            interaction.complexity = request.form.get('complexity')
            interaction.status = request.form.get('status')
            interaction.submitted_by = request.form.get('submitted_by')
            
            db.session.commit()
            flash('Interaction updated successfully!', 'success')
            return redirect(url_for('interaction_detail', interaction_id=interaction_id))
        
        # GET request - show edit form
        tools = ExemplarTool.query.order_by(ExemplarTool.name).all()
        interaction_types = INTERACTION_TYPES

        return render_template('streamlined_edit_interaction.html',
                             interaction=interaction,
                             tools=tools,
                             interaction_types=interaction_types)
    except Exception as e:
        logger.error(f"Error editing interaction: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/export/interactions/csv')
def export_interactions_csv():
    """Export all interactions to CSV format."""
    try:
        interactions = ToolInteraction.query.all()
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Source Tool', 'Target Tool', 'Interaction Type', 'Lifecycle Stage',
            'Description', 'Technical Details', 'Benefits', 'Challenges', 'Examples',
            'Contact Person', 'Organization', 'Email', 'Priority', 'Complexity',
            'Status', 'Submitted By', 'Submitted At', 'Source Tool Open Source',
            'Target Tool Open Source', 'Source Tool URL', 'Target Tool URL'
        ])
        
        # Write data rows
        for interaction in interactions:
            writer.writerow([
                interaction.id,
                interaction.source_tool.name,
                interaction.target_tool.name,
                interaction.interaction_type,
                interaction.lifecycle_stage,
                interaction.description,
                interaction.technical_details or '',
                interaction.benefits or '',
                interaction.challenges or '',
                interaction.examples or '',
                interaction.contact_person or '',
                interaction.organization or '',
                interaction.email or '',
                interaction.priority or '',
                interaction.complexity or '',
                interaction.status or '',
                interaction.submitted_by or '',
                interaction.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if interaction.submitted_at else '',
                'Yes' if interaction.source_tool.is_open_source else 'No',
                'Yes' if interaction.target_tool.is_open_source else 'No',
                interaction.source_tool.url or '',
                interaction.target_tool.url or ''
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=prism_interactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting interactions to CSV: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/download/csv-template')
def download_csv_template():
    """
    Provide a CSV template with example data to help users prepare bulk uploads.

    This template includes:
    - Proper column headers matching database schema
    - Three example rows demonstrating good data quality
    - Different interaction types and lifecycle stages for reference

    Returns:
        CSV file download response
    """
    try:
        # Define template data with high-quality examples
        template_data = [
            {
                'Source Tool': 'GitHub',
                'Target Tool': 'Zenodo',
                'Interaction Type': 'Data Exchange',
                'Lifecycle Stage': 'PRESERVE',
                'Description': 'GitHub repositories can be automatically archived to Zenodo with DOI assignment, creating permanent records of research software and datasets.',
                'Technical Details': 'GitHub webhook integration, automatic metadata transfer via Zenodo API',
                'Benefits': 'Permanent preservation, citable software versions with DOIs, enhanced reproducibility',
                'Challenges': 'Large repository size limits, selective file archiving complexity, metadata mapping',
                'Examples': 'Software packages automatically archived with each GitHub release; Research code preserved with version-specific DOIs',
                'Contact Person': 'Your Name',
                'Organization': 'Your Institution',
                'Email': 'your.email@example.com',
                'Priority': 'medium',
                'Complexity': 'simple',
                'Status': 'implemented',
                'Submitted By': 'Template Example'
            },
            {
                'Source Tool': 'REDCap',
                'Target Tool': 'R',
                'Interaction Type': 'API Integration',
                'Lifecycle Stage': 'ANALYSE',
                'Description': 'REDCap provides direct export capabilities to R for statistical analysis, streamlining the transition from data collection to analysis workflows.',
                'Technical Details': 'REDCap API with R packages (REDCapR, redcapAPI), OAuth authentication, automated data synchronization',
                'Benefits': 'Seamless data workflow, reduced manual errors, reproducible analysis pipelines, real-time data access',
                'Challenges': 'Data format conversion complexity, access control management, API rate limits, authentication setup',
                'Examples': 'Clinical trial data exported from REDCap for statistical analysis in R; Longitudinal study data automatically synced for ongoing analysis',
                'Contact Person': '',
                'Organization': '',
                'Email': '',
                'Priority': 'high',
                'Complexity': 'moderate',
                'Status': 'implemented',
                'Submitted By': 'Template Example'
            },
            {
                'Source Tool': 'Jupyter Notebook',
                'Target Tool': 'Docker',
                'Interaction Type': 'Workflow Integration',
                'Lifecycle Stage': 'ANALYSE',
                'Description': 'Jupyter notebooks can be containerized using Docker to ensure reproducible computational environments across different systems and platforms.',
                'Technical Details': 'Docker containerization, Jupyter Docker stacks, environment specification via Dockerfile',
                'Benefits': 'Reproducible environments, easy deployment, consistent dependencies across systems, version-controlled infrastructure',
                'Challenges': 'Container size optimization, security considerations, learning curve for container technology',
                'Examples': 'Data analysis notebooks packaged as Docker containers for reproducible research; Machine learning workflows containerized for deployment',
                'Contact Person': '',
                'Organization': '',
                'Email': '',
                'Priority': 'medium',
                'Complexity': 'complex',
                'Status': 'implemented',
                'Submitted By': 'Template Example'
            }
        ]

        # Create CSV in memory
        output = StringIO()

        # Define fieldnames matching database schema
        fieldnames = [
            'Source Tool', 'Target Tool', 'Interaction Type', 'Lifecycle Stage',
            'Description', 'Technical Details', 'Benefits', 'Challenges', 'Examples',
            'Contact Person', 'Organization', 'Email', 'Priority', 'Complexity',
            'Status', 'Submitted By'
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(template_data)

        # Prepare response
        csv_content = output.getvalue()
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=prism_interaction_template.csv'

        logger.info("CSV template downloaded successfully")
        return response

    except Exception as e:
        logger.error(f"Error generating CSV template: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/upload/interactions/csv', methods=['GET', 'POST'])
def upload_interactions_csv():
    """Upload interactions from CSV file (without overwriting existing entries)."""
    if request.method == 'GET':
        return render_template('streamlined_upload_csv.html')
    
    try:
        # Check if file was uploaded
        if 'csv_file' not in request.files:
            flash('No file selected. Please choose a CSV file to upload.', 'error')
            return redirect(request.url)
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected. Please choose a CSV file to upload.', 'error')
            return redirect(request.url)
        
        if not file.filename.lower().endswith('.csv'):
            flash('Invalid file type. Please upload a CSV file.', 'error')
            return redirect(request.url)
        
        # Parse CSV content
        stream = StringIO(file.stream.read().decode('utf-8'))
        csv_reader = csv.DictReader(stream)
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        created_tools_count = 0
        errors = []
        created_tools_list = []
        
        # Get all existing interactions for duplicate checking
        existing_interactions = ToolInteraction.query.all()
        existing_signatures = set()
        
        for interaction in existing_interactions:
            # Create signature based on source tool, target tool, and interaction type
            signature = (
                interaction.source_tool_id,
                interaction.target_tool_id, 
                interaction.interaction_type,
                interaction.lifecycle_stage
            )
            existing_signatures.add(signature)
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 to account for header
            try:
                # Skip rows that are missing required fields
                if not all([row.get('Source Tool'), row.get('Target Tool'), 
                           row.get('Interaction Type'), row.get('Lifecycle Stage')]):
                    skipped_count += 1
                    errors.append(f"Row {row_num}: Missing required fields")
                    continue
                
                # Find source and target tools by name, create if not found
                source_tool = ExemplarTool.query.filter_by(name=row['Source Tool']).first()
                target_tool = ExemplarTool.query.filter_by(name=row['Target Tool']).first()
                
                if not source_tool:
                    try:
                        source_tool, created = find_or_create_tool_from_csv(row['Source Tool'], 'CSV Import')
                        created_tools_count += 1
                        created_tools_list.append(f"Row {row_num}: Created source tool '{row['Source Tool']}'")
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: Failed to create source tool '{row['Source Tool']}': {e}")
                        continue
                    
                if not target_tool:
                    try:
                        target_tool, created = find_or_create_tool_from_csv(row['Target Tool'], 'CSV Import')
                        created_tools_count += 1
                        created_tools_list.append(f"Row {row_num}: Created target tool '{row['Target Tool']}'")
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: Failed to create target tool '{row['Target Tool']}': {e}")
                        continue
                
                # Check for duplicates
                signature = (
                    source_tool.id,
                    target_tool.id,
                    row['Interaction Type'],
                    row['Lifecycle Stage']
                )
                
                if signature in existing_signatures:
                    skipped_count += 1
                    errors.append(f"Row {row_num}: Duplicate interaction (same source, target, type, and stage)")
                    continue
                
                # Validate interaction type
                if row['Interaction Type'] not in INTERACTION_TYPES:
                    error_count += 1
                    errors.append(f"Row {row_num}: Invalid interaction type '{row['Interaction Type']}'")
                    continue
                
                # Create new interaction
                interaction = ToolInteraction(
                    source_tool_id=source_tool.id,
                    target_tool_id=target_tool.id,
                    interaction_type=row['Interaction Type'],
                    lifecycle_stage=row['Lifecycle Stage'],
                    description=row.get('Description', ''),
                    technical_details=row.get('Technical Details', ''),
                    benefits=row.get('Benefits', ''),
                    challenges=row.get('Challenges', ''),
                    examples=row.get('Examples', ''),
                    contact_person=row.get('Contact Person', ''),
                    organization=row.get('Organization', ''),
                    email=row.get('Email', ''),
                    priority=row.get('Priority', ''),
                    complexity=row.get('Complexity', ''),
                    status=row.get('Status', ''),
                    submitted_by=row.get('Submitted By', 'CSV Upload'),
                    submitted_at=datetime.now(),
                    auto_created=True  # Mark as auto-created from CSV
                )
                
                db.session.add(interaction)
                existing_signatures.add(signature)  # Add to prevent duplicates within this upload
                imported_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        # Commit all successful imports
        if imported_count > 0:
            db.session.commit()
        
        # Prepare summary message
        messages = []
        if imported_count > 0:
            messages.append(f"Successfully imported {imported_count} interaction(s)")
        if created_tools_count > 0:
            messages.append(f"Auto-created {created_tools_count} new tool(s)")
        if skipped_count > 0:
            messages.append(f"Skipped {skipped_count} duplicate(s)")
        if error_count > 0:
            messages.append(f"Failed to import {error_count} row(s)")
        
        # Show summary
        summary = "; ".join(messages)
        if error_count > 0 or skipped_count > 0:
            flash(f"{summary}. Check details below.", 'warning')
        else:
            flash(summary, 'success')
        
        # Return results page with details
        return render_template('streamlined_upload_results.html', 
                             imported_count=imported_count,
                             skipped_count=skipped_count, 
                             error_count=error_count,
                             created_tools_count=created_tools_count,
                             errors=errors[:20],  # Limit to first 20 errors
                             created_tools=created_tools_list[:20])  # Limit to first 20 created tools
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        flash(f'Error processing CSV file: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/upload/tools/csv', methods=['GET', 'POST'])
def upload_tools_csv():
    """
    Upload and import tools from CSV file.

    Expected CSV columns:
    - Tool Name (required)
    - Description
    - URL
    - Is Open Source (TRUE/FALSE)
    - License
    - GitHub URL
    - Category
    - Stage
    - Notes
    """
    if request.method == 'GET':
        return render_template('streamlined_upload_tools_csv.html')

    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        if not file.filename.endswith('.csv'):
            flash('File must be a CSV', 'error')
            return redirect(request.url)

        # Read CSV file
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)

        # Required column
        required_columns = ['Tool Name']

        # Validate CSV structure
        if not all(col in csv_reader.fieldnames for col in required_columns):
            missing = [col for col in required_columns if col not in csv_reader.fieldnames]
            flash(f'Missing required columns: {", ".join(missing)}', 'error')
            return redirect(request.url)

        # Track statistics
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        errors = []
        updates_list = []

        # Process each row
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            try:
                # Validate required field
                if not row.get('Tool Name', '').strip():
                    error_count += 1
                    errors.append(f"Row {row_num}: Tool Name is required")
                    continue

                tool_name = row['Tool Name'].strip()

                # Check if tool already exists
                existing_tool = ExemplarTool.query.filter_by(name=tool_name).first()

                # Parse Is Open Source
                is_open_source = None
                if row.get('Is Open Source', '').strip().upper() == 'TRUE':
                    is_open_source = True
                elif row.get('Is Open Source', '').strip().upper() == 'FALSE':
                    is_open_source = False

                # Note: We don't create/update categories from CSV since they require stage_id
                # Categories must be created through the normal UI which associates them with stages

                if existing_tool:
                    # Update existing tool with enriched data
                    updated = False

                    if row.get('Description', '').strip() and not existing_tool.description:
                        existing_tool.description = row['Description'].strip()
                        updated = True

                    if row.get('URL', '').strip() and not existing_tool.url:
                        existing_tool.url = row['URL'].strip()
                        updated = True

                    if is_open_source is not None:
                        existing_tool.is_open_source = is_open_source
                        updated = True

                    # Update new enriched fields
                    if row.get('License', '').strip() and not existing_tool.license:
                        existing_tool.license = row['License'].strip()
                        updated = True

                    if row.get('GitHub URL', '').strip() and not existing_tool.github_url:
                        existing_tool.github_url = row['GitHub URL'].strip()
                        updated = True

                    if row.get('Notes', '').strip():
                        # Append notes if they don't already exist
                        if not existing_tool.notes or row['Notes'].strip() not in existing_tool.notes:
                            existing_tool.notes = (existing_tool.notes or '') + '\n' + row['Notes'].strip()
                            updated = True

                    if updated:
                        updated_count += 1
                        updates_list.append(f"Row {row_num}: Updated tool '{tool_name}'")
                    else:
                        skipped_count += 1
                else:
                    # Create new tool with enriched fields
                    # Now stage_id and category_id are nullable, so we can create tools from CSV
                    new_tool = ExemplarTool(
                        name=tool_name,
                        description=row.get('Description', '').strip() or None,
                        url=row.get('URL', '').strip() or None,
                        is_open_source=is_open_source,
                        license=row.get('License', '').strip() or None,
                        github_url=row.get('GitHub URL', '').strip() or None,
                        notes=row.get('Notes', '').strip() or None,
                        stage_id=None,  # Will be set via UI later
                        category_id=None,  # Will be set via UI later
                        auto_created=True,  # Mark as auto-created
                        created_via='CSV Import',
                        import_source='Tool CSV Upload'
                    )

                    db.session.add(new_tool)
                    imported_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"Row {row_num}: {str(e)}")
                continue

        # Commit all successful imports/updates
        if imported_count > 0 or updated_count > 0:
            db.session.commit()

        # Prepare summary message
        messages = []
        if imported_count > 0:
            messages.append(f"Successfully imported {imported_count} new tool(s)")
        if updated_count > 0:
            messages.append(f"Updated {updated_count} existing tool(s)")
        if skipped_count > 0:
            messages.append(f"Skipped {skipped_count} tool(s) (no changes)")
        if error_count > 0:
            messages.append(f"Failed to import {error_count} row(s)")

        # Show summary
        summary = "; ".join(messages)
        if error_count > 0 or skipped_count > 0:
            flash(f"{summary}. Check details below.", 'warning')
        else:
            flash(summary, 'success')

        # Return results page with details
        return render_template('streamlined_upload_tools_results.html',
                             imported_count=imported_count,
                             updated_count=updated_count,
                             skipped_count=skipped_count,
                             error_count=error_count,
                             errors=errors[:20],  # Limit to first 20 errors
                             updates=updates_list[:20])  # Limit to first 20 updates

    except Exception as e:
        logger.error(f"Error uploading tools CSV: {e}")
        flash(f'Error processing CSV file: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/about')
def about():
    """About page with MaLDReTH II and RDA context."""
    return render_template('about.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Collect user feedback on PRISM alpha."""
    if request.method == 'POST':
        try:
            # Collect feedback data
            new_feedback = Feedback(
                category=request.form.get('category'),
                feedback_text=request.form.get('feedback_text'),
                page_url=request.form.get('page_url', request.referrer),
                contact_name=request.form.get('contact_name'),
                contact_email=request.form.get('contact_email'),
                user_agent=request.headers.get('User-Agent')
            )

            db.session.add(new_feedback)
            db.session.commit()

            logger.info(f"Feedback received: Category={new_feedback.category}, ID={new_feedback.id}")
            flash('Thank you for your feedback! Your input helps us improve PRISM.', 'success')

            return redirect(url_for('feedback'))
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            flash('An error occurred while submitting your feedback. Please try again.', 'danger')
            db.session.rollback()

    # GET request - show form
    return render_template('feedback.html')

@app.route('/feedback/review')
def review_feedback():
    """Admin view to review all submitted feedback."""
    try:
        # Get all feedback, ordered by most recent first
        all_feedback = Feedback.query.order_by(Feedback.submitted_at.desc()).all()

        # Get summary statistics
        total_count = len(all_feedback)
        status_counts = {
            'new': len([f for f in all_feedback if f.status == 'new']),
            'reviewed': len([f for f in all_feedback if f.status == 'reviewed']),
            'addressed': len([f for f in all_feedback if f.status == 'addressed'])
        }
        category_counts = {}
        for f in all_feedback:
            category_counts[f.category] = category_counts.get(f.category, 0) + 1

        return render_template('feedback_review.html',
                             feedback_items=all_feedback,
                             total_count=total_count,
                             status_counts=status_counts,
                             category_counts=category_counts)
    except Exception as e:
        logger.error(f"Error reviewing feedback: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/quick-add', methods=['GET', 'POST'])
def quick_add_interaction():
    """Quick entry form for adding tool interactions with minimal required fields."""
    if request.method == 'POST':
        try:
            # Create new interaction with only required fields
            new_interaction = ToolInteraction(
                source_tool_id=request.form['source_tool_id'],
                target_tool_id=request.form['target_tool_id'],
                interaction_type=request.form['interaction_type'],
                lifecycle_stage=request.form['lifecycle_stage'],
                description=request.form['description'],
                submitted_by=request.form.get('submitted_by', 'Anonymous')
            )

            db.session.add(new_interaction)
            db.session.commit()

            logger.info(f"Quick interaction added: {new_interaction.interaction_type} between {new_interaction.source_tool.name} and {new_interaction.target_tool.name}")

            # Check if user wants to add another
            if request.form.get('add_another') == 'true':
                flash('Interaction added successfully! Add another below.', 'success')
                return redirect(url_for('quick_add_interaction'))
            else:
                flash('Interaction added successfully!', 'success')
                return redirect(url_for('view_interactions'))

        except Exception as e:
            logger.error(f"Error adding quick interaction: {e}")
            flash('An error occurred while adding the interaction. Please try again.', 'danger')
            db.session.rollback()

    # GET request - show form
    all_tools = ExemplarTool.query.filter_by(is_active=True).order_by(ExemplarTool.name).all()

    return render_template('quick_add.html',
                         tools=all_tools,
                         interaction_types=INTERACTION_TYPES,
                         lifecycle_stages=LIFECYCLE_STAGES)

@app.route('/glossary')
def glossary():
    """
    Comprehensive glossary and terminology reference page.

    FAQ and terminology can be updated in config/glossary_content.py
    without modifying this code.
    """
    try:
        # Get all stages with their definitions
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()

        # Get statistics for context
        total_interactions = ToolInteraction.query.count()
        total_tools = ExemplarTool.query.count()

        # Get interaction type usage statistics
        interaction_type_stats = {}
        for itype in INTERACTION_TYPES:
            count = ToolInteraction.query.filter_by(interaction_type=itype).count()
            interaction_type_stats[itype] = count

        return render_template('glossary.html',
                             interaction_types=INTERACTION_TYPE_DEFINITIONS,
                             lifecycle_stages=LIFECYCLE_STAGE_DEFINITIONS,
                             stages=stages,
                             interaction_type_stats=interaction_type_stats,
                             total_interactions=total_interactions,
                             total_tools=total_tools,
                             faq_items=FAQ_ITEMS,
                             maldreth_terminology=MALDRETH_TERMINOLOGY,
                             glossary_config_loaded=GLOSSARY_CONFIG_LOADED)
    except Exception as e:
        logger.error(f"Error in glossary route: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/user-guide')
def user_guide():
    """
    Interactive user guide for adding and curating interactions.

    Comprehensive documentation covering:
    - Understanding tool interactions
    - Web form submission
    - CSV bulk import
    - Curation best practices
    - Troubleshooting and support
    """
    try:
        # Get statistics for contextual examples
        total_interactions = ToolInteraction.query.count()
        total_tools = ExemplarTool.query.count()
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()

        return render_template('user_guide.html',
                             interaction_types=INTERACTION_TYPES,
                             lifecycle_stages=LIFECYCLE_STAGES,
                             stages=stages,
                             total_interactions=total_interactions,
                             total_tools=total_tools)
    except Exception as e:
        logger.error(f"Error in user guide route: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/information-structures')
def information_structures():
    """Information Structures page with database schema and live data visualization."""
    try:
        # Get database statistics
        stats = {
            'total_interactions': ToolInteraction.query.count(),
            'total_tools': ExemplarTool.query.count(),
            'total_stages': MaldrethStage.query.count(),
            'total_categories': ToolCategory.query.count(),
        }
        
        # Get interaction type distribution
        interaction_types = db.session.query(
            ToolInteraction.interaction_type,
            db.func.count(ToolInteraction.id).label('count')
        ).group_by(ToolInteraction.interaction_type).all()
        
        # Get lifecycle stage distribution
        stage_distribution = db.session.query(
            ToolInteraction.lifecycle_stage,
            db.func.count(ToolInteraction.id).label('count')
        ).group_by(ToolInteraction.lifecycle_stage).all()
        
        # Get tool usage in interactions (with error handling for empty database)
        try:
            tool_usage = db.session.query(
                ExemplarTool.name,
                db.func.count(ToolInteraction.id).label('count')
            ).join(
                ToolInteraction,
                db.or_(
                    ToolInteraction.source_tool_id == ExemplarTool.id,
                    ToolInteraction.target_tool_id == ExemplarTool.id
                )
            ).group_by(ExemplarTool.name).order_by(
                db.func.count(ToolInteraction.id).desc()
            ).limit(10).all()
        except Exception as e:
            logger.warning(f"Could not get tool usage: {e}")
            tool_usage = []

        # Get recent interactions (with error handling)
        try:
            recent_interactions = ToolInteraction.query.order_by(
                ToolInteraction.submitted_at.desc()
            ).limit(5).all()
        except Exception as e:
            logger.warning(f"Could not get recent interactions: {e}")
            recent_interactions = []
        
        # Get all stages with their tool counts
        stages_with_tools = []
        for stage in MaldrethStage.query.order_by(MaldrethStage.position).all():
            tool_count = ExemplarTool.query.join(ToolCategory).filter(
                ToolCategory.stage_id == stage.id
            ).count()
            stages_with_tools.append({
                'stage': stage,
                'tool_count': tool_count
            })
        
        return render_template('information_structures.html',
                             stats=stats,
                             interaction_types=interaction_types,
                             stage_distribution=stage_distribution,
                             tool_usage=tool_usage,
                             recent_interactions=recent_interactions,
                             stages_with_tools=stages_with_tools)
    except Exception as e:
        logger.error(f"Error loading information structures: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/rdl')
def rdl_overview():
    """Display the MaLDReTH Research Data Lifecycle overview with actual tools."""
    try:
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        
        # Get comprehensive stage data with tools
        stage_data = {}
        for stage in stages:
            # Get tools for this stage
            tools = ExemplarTool.query.filter_by(stage_id=stage.id, is_active=True).order_by(ExemplarTool.name).limit(10).all()
            
            # Count interactions where either source or target tool belongs to this stage
            source_count = ToolInteraction.query.join(ExemplarTool, ToolInteraction.source_tool_id == ExemplarTool.id).filter(ExemplarTool.stage_id == stage.id).count()
            target_count = ToolInteraction.query.join(ExemplarTool, ToolInteraction.target_tool_id == ExemplarTool.id).filter(ExemplarTool.stage_id == stage.id).count()
            
            # Get tool categories for this stage
            categories = ToolCategory.query.filter_by(stage_id=stage.id).all()
            
            stage_data[stage.id] = {
                'source_interactions': source_count,
                'target_interactions': target_count,
                'total_interactions': source_count + target_count,
                'tool_count': ExemplarTool.query.filter_by(stage_id=stage.id, is_active=True).count(),
                'category_count': len(categories),
                'tools': tools,
                'categories': categories,
                'has_more_tools': ExemplarTool.query.filter_by(stage_id=stage.id, is_active=True).count() > 10
            }
        
        return render_template('rdl_overview.html', stages=stages, stage_stats=stage_data)
    except Exception as e:
        logger.error(f"Error viewing RDL overview: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/rdl/visualization')
def rdl_visualization():
    """Display interactive visualization of the MaLDReTH RDL with interactions."""
    try:
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        interactions = ToolInteraction.query.all()
        
        # Prepare data for visualization
        visualization_data = {
            'stages': [],
            'interactions': [],
            'tools': []
        }
        
        # Stage data
        for stage in stages:
            stage_data = {
                'id': stage.id,
                'name': stage.name,
                'position': stage.position,
                'description': stage.description,
                'tool_count': ExemplarTool.query.filter_by(stage_id=stage.id).count(),
                'category_count': ToolCategory.query.filter_by(stage_id=stage.id).count()
            }
            visualization_data['stages'].append(stage_data)
        
        # Tool data
        tools = ExemplarTool.query.all()
        for tool in tools:
            # Skip tools without stage/category (e.g., CSV imported tools)
            if not tool.category or not tool.stage_id:
                continue

            tool_data = {
                'id': tool.id,
                'name': tool.name,
                'stage_id': tool.stage_id,
                'stage_name': tool.category.stage.name,
                'category': tool.category.name
            }
            visualization_data['tools'].append(tool_data)
        
        # Interaction data
        for interaction in interactions:
            interaction_data = {
                'id': interaction.id,
                'source_tool_id': interaction.source_tool_id,
                'target_tool_id': interaction.target_tool_id,
                'source_tool_name': interaction.source_tool.name,
                'target_tool_name': interaction.target_tool.name,
                'source_stage_id': interaction.source_tool.stage_id,
                'target_stage_id': interaction.target_tool.stage_id,
                'interaction_type': interaction.interaction_type,
                'lifecycle_stage': interaction.lifecycle_stage,
                'description': interaction.description[:100] + '...' if len(interaction.description) > 100 else interaction.description,
                'status': interaction.status or 'unknown'
            }
            visualization_data['interactions'].append(interaction_data)
        
        return render_template('rdl_visualization.html', 
                             stages=visualization_data['stages'], 
                             visualization_data=visualization_data)
    except Exception as e:
        logger.error(f"Error in RDL visualization: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/enhanced-rdl-visualization')
def enhanced_rdl_visualization():
    """Display enhanced interactive visualization based on MaLDReTH 1 patterns."""
    try:
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        tools = ExemplarTool.query.filter_by(is_active=True).all()
        interactions = ToolInteraction.query.all()
        
        # Prepare comprehensive data for enhanced visualization
        stage_list = []
        tool_list = []
        interaction_list = []
        
        # Enhanced stage data with colors and statistics
        stage_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD',
            '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
        ]
        
        for i, stage in enumerate(stages):
            stage_tools = [t for t in tools if t.stage_id == stage.id]
            
            stage_data = {
                'id': stage.id,
                'name': stage.name,
                'description': stage.description or f"Stage {stage.position + 1} of the research data lifecycle",
                'position': stage.position,
                'color': stage_colors[i % len(stage_colors)],
                'tool_count': len(stage_tools),
                'tools': [{'id': t.id, 'name': t.name, 'is_open_source': t.is_open_source} for t in stage_tools]
            }
            stage_list.append(stage_data)
        
        # Enhanced tool data
        for tool in tools:
            tool_data = {
                'id': tool.id,
                'name': tool.name,
                'description': tool.description or f"Research tool: {tool.name}",
                'url': tool.url,
                'stage_id': tool.stage_id,
                'category_id': tool.category_id,
                'is_open_source': tool.is_open_source,
                'is_active': tool.is_active,
                'provider': getattr(tool, 'provider', 'Unknown'),
                'auto_created': getattr(tool, 'auto_created', False)
            }
            tool_list.append(tool_data)
        
        # Enhanced interaction data with safer relationship access
        for interaction in interactions:
            try:
                # Safer way to get tool names
                source_tool_name = 'Unknown'
                target_tool_name = 'Unknown'
                
                if interaction.source_tool_id:
                    source_tool = ExemplarTool.query.get(interaction.source_tool_id)
                    if source_tool:
                        source_tool_name = source_tool.name
                
                if interaction.target_tool_id:
                    target_tool = ExemplarTool.query.get(interaction.target_tool_id)
                    if target_tool:
                        target_tool_name = target_tool.name
                
                interaction_data = {
                    'id': interaction.id,
                    'source_tool_id': interaction.source_tool_id,
                    'target_tool_id': interaction.target_tool_id,
                    'source_tool_name': source_tool_name,
                    'target_tool_name': target_tool_name,
                    'interaction_type': interaction.interaction_type,
                    'lifecycle_stage': interaction.lifecycle_stage,
                    'description': interaction.description,
                    'priority': getattr(interaction, 'priority', 'Medium'),
                    'status': getattr(interaction, 'status', 'Active')
                }
                interaction_list.append(interaction_data)
            except Exception as e:
                logger.warning(f"Error processing interaction {interaction.id}: {e}")
                continue
        
        # Calculate summary statistics
        total_tools = len(tool_list)
        total_interactions = len(interaction_list)
        open_source_tools = len([t for t in tool_list if t['is_open_source']])
        auto_created_tools = len([t for t in tool_list if t['auto_created']])
        
        return render_template('enhanced_rdl_visualization.html',
                             stages=stage_list,
                             tools=tool_list,
                             interactions=interaction_list,
                             total_tools=total_tools,
                             total_interactions=total_interactions,
                             open_source_tools=open_source_tools,
                             auto_created_tools=auto_created_tools)
                             
    except Exception as e:
        logger.error(f"Error in enhanced RDL visualization: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/simple-maldreth-visualization')
def simple_maldreth_visualization():
    """Display simple MaLDReTH visualization based on official deliverable patterns."""
    try:
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        tools = ExemplarTool.query.filter_by(is_active=True).all()
        
        # Prepare simplified visualization data
        visualization_data = {
            'stages': [],
            'total_stages': len(stages),
            'total_tools': len(tools)
        }
        
        # Create serializable stage data for JavaScript
        for stage in stages:
            stage_tools = [t for t in tools if t.stage_id == stage.id]
            stage_data = {
                'id': stage.id,
                'name': stage.name,
                'description': stage.description,
                'position': stage.position,
                'color': stage.color,
                'tool_count': len(stage_tools)
            }
            visualization_data['stages'].append(stage_data)
        
        return render_template('simple_maldreth_visualization.html',
                             stages=stages,
                             stages_json=visualization_data['stages'],
                             visualization_data=visualization_data)
                             
    except Exception as e:
        logger.error(f"Error in simple MaLDReTH visualization: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/css-rdl-visualization')
def css_rdl_visualization():
    """Display CSS-only RDL visualization - no external dependencies required."""
    try:
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        tools = ExemplarTool.query.filter_by(is_active=True).all()
        
        # Prepare visualization data
        visualization_data = {
            'stages': [],
            'total_stages': len(stages),
            'total_tools': len(tools)
        }
        
        # Create serializable stage data
        for stage in stages:
            stage_tools = [t for t in tools if t.stage_id == stage.id]
            stage_data = {
                'id': stage.id,
                'name': stage.name,
                'description': stage.description,
                'position': stage.position,
                'tool_count': len(stage_tools)
            }
            visualization_data['stages'].append(stage_data)
        
        return render_template('css_rdl_visualization.html',
                             stages=stages,
                             visualization_data=visualization_data)
                             
    except Exception as e:
        logger.error(f"Error in CSS RDL visualization: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/radial-visualization')
def radial_visualization():
    """Advanced radial visualization showing tool interactions across the lifecycle."""
    try:
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        categories = ToolCategory.query.all()
        tools = ExemplarTool.query.filter_by(is_active=True).all()
        interactions = ToolInteraction.query.all()

        return render_template('radial_visualization.html',
                             total_stages=len(stages),
                             total_categories=len(categories),
                             total_tools=len(tools),
                             total_interactions=len(interactions))
    except Exception as e:
        logger.error(f"Error in radial visualization: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/radial-visualization-data')
def radial_visualization_data():
    """API endpoint providing data for the radial visualization."""
    try:
        # Get all stages in order
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        stage_names = [stage.name for stage in stages]

        # Get all categories with their tools
        categories = ToolCategory.query.all()
        gorc_categories = []

        for category in categories:
            category_data = {
                'name': category.name,
                'stage': category.stage.name if category.stage else 'Unknown',
                'tools': []
            }

            # Get tools for this category
            tools = ExemplarTool.query.filter_by(category_id=category.id, is_active=True).all()
            for tool in tools:
                category_data['tools'].append({
                    'name': tool.name,
                    'description': tool.description or '',
                    'url': tool.url or '',
                    'provider': tool.provider or ''
                })

            gorc_categories.append(category_data)

        # Build correlations (which categories appear in which stages)
        correlations = {}
        for category in categories:
            correlations[category.name] = {}
            for stage_name in stage_names:
                # Check if category belongs to this stage
                if category.stage and category.stage.name == stage_name:
                    correlations[category.name][stage_name] = {
                        'marker': 'XX',  # Strong correlation (primary stage)
                        'description': f'{category.name} tools for {stage_name}'
                    }
                else:
                    # Check if any tools in this category have interactions with this stage
                    has_interaction = False
                    for tool in category.tools:
                        if tool.is_active:
                            # Check interactions as source or target
                            source_interactions = ToolInteraction.query.filter_by(
                                source_tool_id=tool.id,
                                lifecycle_stage=stage_name
                            ).count()
                            target_interactions = ToolInteraction.query.filter_by(
                                target_tool_id=tool.id,
                                lifecycle_stage=stage_name
                            ).count()

                            if source_interactions > 0 or target_interactions > 0:
                                has_interaction = True
                                break

                    if has_interaction:
                        correlations[category.name][stage_name] = {
                            'marker': 'X',  # Weak correlation (has interactions)
                            'description': f'{category.name} has tool interactions in {stage_name}'
                        }
                    else:
                        correlations[category.name][stage_name] = {
                            'marker': '',
                            'description': ''
                        }

        # Get actual tools per stage (not just counts) for visualization
        stage_tools = {}
        for stage in stages:
            tools = ExemplarTool.query.filter_by(stage_id=stage.id, is_active=True).all()
            stage_tools[stage.name] = []
            for tool in tools:
                stage_tools[stage.name].append({
                    'name': tool.name,
                    'category': tool.category.name if tool.category else 'Uncategorized',
                    'description': tool.description or '',
                    'url': tool.url or '',
                    'provider': tool.provider or ''
                })

        # Prepare response data
        response_data = {
            'stages': stage_names,
            'gorcCategories': gorc_categories,
            'correlations': correlations,
            'stageTools': stage_tools
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error generating radial visualization data: {e}")
        return jsonify({'error': str(e)}), 500

# --- Tool Management Routes ---

@app.route('/add-tool', methods=['GET', 'POST'])
def add_tool():
    """Add a new tool to the database."""
    stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
    categories = ToolCategory.query.all()
    
    if request.method == 'POST':
        try:
            # Get selected category and its stage
            category_id = int(request.form.get('category_id'))
            category = ToolCategory.query.get_or_404(category_id)
            
            tool = ExemplarTool(
                name=request.form.get('name'),
                description=request.form.get('description'),
                url=request.form.get('url'),
                provider=request.form.get('provider'),
                stage_id=category.stage_id,
                category_id=category_id,
                is_open_source=bool(request.form.get('is_open_source')),
                is_active=True,
                auto_created=False,
                import_source='Manual Entry'
            )
            
            db.session.add(tool)
            db.session.commit()
            flash(f'Tool "{tool.name}" added successfully!', 'success')
            return redirect(url_for('tool_detail', tool_id=tool.id))
            
        except Exception as e:
            logger.error(f"Error adding tool: {e}")
            db.session.rollback()
            flash('Error adding tool. Please try again.', 'error')
    
    return render_template('streamlined_add_tool.html', 
                         stages=stages, 
                         categories=categories)

@app.route('/tool/<int:tool_id>')
def tool_detail(tool_id):
    """Display details for a specific tool."""
    try:
        tool = ExemplarTool.query.get_or_404(tool_id)
        
        # Get interaction counts
        source_interactions = tool.source_interactions.count()
        target_interactions = tool.target_interactions.count()
        total_interactions = source_interactions + target_interactions
        
        # Get recent interactions (last 5)
        recent_interactions = ToolInteraction.query.filter(
            (ToolInteraction.source_tool_id == tool_id) | 
            (ToolInteraction.target_tool_id == tool_id)
        ).order_by(ToolInteraction.submitted_at.desc()).limit(5).all()
        
        return render_template('streamlined_tool_detail.html',
                             tool=tool,
                             source_interactions=source_interactions,
                             target_interactions=target_interactions,
                             total_interactions=total_interactions,
                             recent_interactions=recent_interactions)
    except Exception as e:
        logger.error(f"Error displaying tool detail: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/tool/<int:tool_id>/edit', methods=['GET', 'POST'])
def edit_tool(tool_id):
    """Edit an existing tool."""
    try:
        tool = ExemplarTool.query.get_or_404(tool_id)
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        categories = ToolCategory.query.all()
        
        if request.method == 'POST':
            # Get selected category and its stage
            category_id = int(request.form.get('category_id'))
            category = ToolCategory.query.get_or_404(category_id)
            
            # Update tool fields
            tool.name = request.form.get('name')
            tool.description = request.form.get('description')
            tool.url = request.form.get('url')
            tool.provider = request.form.get('provider')
            tool.stage_id = category.stage_id
            tool.category_id = category_id
            tool.is_open_source = bool(request.form.get('is_open_source'))
            tool.is_active = bool(request.form.get('is_active'))
            
            db.session.commit()
            flash(f'Tool "{tool.name}" updated successfully!', 'success')
            return redirect(url_for('tool_detail', tool_id=tool_id))
        
        return render_template('streamlined_edit_tool.html',
                             tool=tool,
                             stages=stages,
                             categories=categories)
    except Exception as e:
        logger.error(f"Error editing tool: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/tools')
def view_tools():
    """Display all tools with search and filter capabilities."""
    try:
        # Get filter parameters
        stage_filter = request.args.get('stage')
        category_filter = request.args.get('category')
        search = request.args.get('search', '').strip()
        show_auto_created = request.args.get('auto_created') == 'true'
        
        # Base query
        query = ExemplarTool.query.filter_by(is_active=True)
        
        # Apply filters
        if stage_filter:
            query = query.filter(ExemplarTool.stage_id == stage_filter)
        
        if category_filter:
            query = query.filter(ExemplarTool.category_id == category_filter)
            
        if search:
            query = query.filter(
                ExemplarTool.name.ilike(f'%{search}%') |
                ExemplarTool.description.ilike(f'%{search}%') |
                ExemplarTool.provider.ilike(f'%{search}%')
            )
        
        if show_auto_created:
            query = query.filter(ExemplarTool.auto_created == True)
        
        tools = query.order_by(ExemplarTool.name).all()
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        
        # Get all categories for JavaScript filtering, but filter displayed ones
        all_categories = ToolCategory.query.order_by(ToolCategory.name).all()
        if stage_filter:
            displayed_categories = [cat for cat in all_categories if str(cat.stage_id) == stage_filter]
        else:
            displayed_categories = all_categories
        
        return render_template('streamlined_view_tools.html',
                             tools=tools,
                             stages=stages,
                             categories=displayed_categories,
                             all_categories=all_categories,  # For JavaScript
                             current_stage=stage_filter,
                             current_category=category_filter,
                             current_search=search,
                             show_auto_created=show_auto_created)
    except Exception as e:
        logger.error(f"Error viewing tools: {e}")
        return render_template('error.html', error=str(e)), 500

# --- API Routes ---

@app.route('/api/tool/<int:tool_id>/stage')
def get_tool_stage(tool_id):
    """Get the lifecycle stage for a specific tool."""
    try:
        tool = ExemplarTool.query.get_or_404(tool_id)
        return jsonify({
            'stage_name': tool.category.stage.name,
            'stage_id': tool.category.stage.id
        })
    except Exception as e:
        logger.error(f"Error getting tool stage: {e}")
        return jsonify({'error': 'Tool not found'}), 404

@app.route('/api/v1/tools')
def api_get_tools():
    """API endpoint to retrieve all tools with their properties."""
    try:
        tools = ExemplarTool.query.filter_by(is_active=True).all()
        tools_data = []
        
        for tool in tools:
            # Build tool data safely, handling missing fields
            tool_data = {
                'id': tool.id,
                'name': tool.name,
                'description': tool.description,
                'url': tool.url,
                'is_open_source': tool.is_open_source,
                'stage': {
                    'id': tool.category.stage.id,
                    'name': tool.category.stage.name,
                    'position': tool.category.stage.position
                },
            }
            
            # Add new fields if they exist
            try:
                tool_data['provider'] = getattr(tool, 'provider', None)
                tool_data['auto_created'] = getattr(tool, 'auto_created', False)
                tool_data['import_source'] = getattr(tool, 'import_source', None)
                tool_data['created_at'] = tool.created_at.isoformat() if hasattr(tool, 'created_at') and tool.created_at else None
                tool_data['updated_at'] = tool.updated_at.isoformat() if hasattr(tool, 'updated_at') and tool.updated_at else None
            except AttributeError:
                # Fields don't exist in this schema version
                tool_data['provider'] = None
                tool_data['auto_created'] = False
                tool_data['import_source'] = None
                tool_data['created_at'] = None
                tool_data['updated_at'] = None
            
            # Add category information
            tool_data['category'] = {
                'id': tool.category.id,
                'name': tool.category.name,
                'description': tool.category.description
            }
            
            tools_data.append(tool_data)
        
        return jsonify({
            'success': True,
            'count': len(tools_data),
            'tools': tools_data
        })
    except Exception as e:
        logger.error(f"Error in API get tools: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/v1/interactions')
def api_get_interactions():
    """API endpoint to retrieve all interactions with detailed information."""
    try:
        interactions = ToolInteraction.query.all()
        interactions_data = []
        
        for interaction in interactions:
            interactions_data.append({
                'id': interaction.id,
                'interaction_type': interaction.interaction_type,
                'lifecycle_stage': interaction.lifecycle_stage,
                'description': interaction.description,
                'technical_details': interaction.technical_details,
                'benefits': interaction.benefits,
                'challenges': interaction.challenges,
                'examples': interaction.examples,
                'priority': interaction.priority,
                'complexity': interaction.complexity,
                'status': interaction.status,
                'submitted_at': interaction.submitted_at.isoformat() if interaction.submitted_at else None,
                'source_tool': {
                    'id': interaction.source_tool.id,
                    'name': interaction.source_tool.name,
                    'is_open_source': interaction.source_tool.is_open_source,
                    'url': interaction.source_tool.url
                },
                'target_tool': {
                    'id': interaction.target_tool.id,
                    'name': interaction.target_tool.name,
                    'is_open_source': interaction.target_tool.is_open_source,
                    'url': interaction.target_tool.url
                }
            })
        
        return jsonify({
            'success': True,
            'count': len(interactions_data),
            'interactions': interactions_data
        })
    except Exception as e:
        logger.error(f"Error in API get interactions: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/v1/statistics')
def api_get_statistics():
    """API endpoint to retrieve PRISM platform statistics."""
    try:
        stats = {
            'total_tools': ExemplarTool.query.filter_by(is_active=True).count(),
            'total_interactions': ToolInteraction.query.count(),
            'total_stages': MaldrethStage.query.count(),
            'open_source_tools': ExemplarTool.query.filter_by(is_active=True, is_open_source=True).count(),
            'interaction_types': {},
            'stage_distribution': {}
        }
        
        # Count interactions by type
        for interaction_type in INTERACTION_TYPES:
            count = ToolInteraction.query.filter_by(interaction_type=interaction_type).count()
            if count > 0:
                stats['interaction_types'][interaction_type] = count
        
        # Count tools by stage
        for stage in MaldrethStage.query.all():
            tool_count = ExemplarTool.query.filter_by(stage_id=stage.id, is_active=True).count()
            stats['stage_distribution'][stage.name] = tool_count
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error in API get statistics: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/export/csv')
def export_csv():
    """Export all interactions to CSV format."""
    try:
        import csv
        from io import StringIO
        from flask import make_response
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Source Tool', 'Target Tool', 'Interaction Type', 'Lifecycle Stage',
            'Description', 'Technical Details', 'Benefits', 'Challenges', 'Examples',
            'Contact Person', 'Organization', 'Email', 'Priority', 'Complexity', 
            'Status', 'Submitted By', 'Submitted At'
        ])
        
        # Write data
        interactions = ToolInteraction.query.all()
        for interaction in interactions:
            writer.writerow([
                interaction.id,
                interaction.source_tool.name,
                interaction.target_tool.name,
                interaction.interaction_type,
                interaction.lifecycle_stage,
                interaction.description,
                interaction.technical_details or '',
                interaction.benefits or '',
                interaction.challenges or '',
                interaction.examples or '',
                interaction.contact_person or '',
                interaction.organization or '',
                interaction.email or '',
                interaction.priority or '',
                interaction.complexity or '',
                interaction.status or '',
                interaction.submitted_by or '',
                interaction.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if interaction.submitted_at else ''
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=maldreth_interactions.csv'
        return response
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        flash('Error exporting data. Please try again.', 'error')
        return redirect(url_for('index'))


# --- Database Initialization ---

def migrate_database_schema():
    """Safely migrate database schema to add new fields without data loss."""
    try:
        # Check if new columns exist and add them if they don't
        inspector = db.inspect(db.engine)

        # Check if exemplar_tools table exists
        tables = inspector.get_table_names()
        if 'exemplar_tools' not in tables:
            logger.info("Tables don't exist yet, creating all tables...")
            db.create_all()
            logger.info("✅ Database tables created successfully")
            return

        # Check if feedback table exists (added for Phase 1 feedback collection)
        if 'feedback' not in tables:
            logger.info("Feedback table missing, creating it...")
            # Create only the Feedback table
            Feedback.__table__.create(db.engine, checkfirst=True)
            logger.info("✅ Feedback table created successfully")

        columns = [col['name'] for col in inspector.get_columns('exemplar_tools')]
        
        migrations_needed = []
        
        # Check for each new column and add SQL to create them
        if 'provider' not in columns:
            migrations_needed.append('ALTER TABLE exemplar_tools ADD COLUMN provider VARCHAR(200)')
        if 'auto_created' not in columns:
            migrations_needed.append('ALTER TABLE exemplar_tools ADD COLUMN auto_created BOOLEAN DEFAULT FALSE')
        if 'import_source' not in columns:
            migrations_needed.append('ALTER TABLE exemplar_tools ADD COLUMN import_source VARCHAR(100)')
        if 'created_at' not in columns:
            migrations_needed.append('ALTER TABLE exemplar_tools ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        if 'updated_at' not in columns:
            migrations_needed.append('ALTER TABLE exemplar_tools ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        # Check tool_interactions table for enhanced visualization fields
        try:
            interaction_columns = [col['name'] for col in inspector.get_columns('tool_interactions')]
            if 'priority' not in interaction_columns:
                migrations_needed.append("ALTER TABLE tool_interactions ADD COLUMN priority VARCHAR(20) DEFAULT 'Medium'")
            if 'complexity' not in interaction_columns:
                migrations_needed.append("ALTER TABLE tool_interactions ADD COLUMN complexity VARCHAR(20) DEFAULT 'Medium'")
            if 'status' not in interaction_columns:
                migrations_needed.append("ALTER TABLE tool_interactions ADD COLUMN status VARCHAR(20) DEFAULT 'Active'")

            # Nov 13, 2025 Co-chairs meeting: Make lifecycle_stage nullable (now computed from tools)
            if 'lifecycle_stage' in interaction_columns:
                # Check if column info has nullable property
                col_info = [col for col in inspector.get_columns('tool_interactions') if col['name'] == 'lifecycle_stage']
                if col_info and not col_info[0].get('nullable', False):
                    logger.info("Migrating lifecycle_stage to nullable (now auto-computed)...")
                    migrations_needed.append("ALTER TABLE tool_interactions ALTER COLUMN lifecycle_stage DROP NOT NULL")

        except Exception as e:
            logger.warning(f"Could not check tool_interactions table: {e}")
        
        # Execute migrations
        for migration in migrations_needed:
            logger.info(f"Executing migration: {migration}")
            try:
                db.session.execute(db.text(migration))
            except Exception as e:
                logger.error(f"Failed to execute migration {migration}: {e}")
                continue
        
        if migrations_needed:
            try:
                db.session.commit()
                logger.info(f"Successfully applied {len(migrations_needed)} schema migrations")
            except Exception as e:
                logger.error(f"Failed to commit migrations: {e}")
                db.session.rollback()
        else:
            logger.info("Database schema is up to date")
            
    except Exception as e:
        logger.error(f"Error during schema migration: {e}")
        db.session.rollback()

def init_database_with_maldreth_data():
    """Initialize database with MaLDReTH 1.0 data, preventing duplicates."""
    logger.info("Starting database initialization with duplicate prevention...")
    
    # Check if data already exists (skip if already populated)
    existing_stages = MaldrethStage.query.count()
    existing_tools = ExemplarTool.query.filter_by(is_active=True).count()
    
    if existing_stages >= 12 and existing_tools > 50:
        logger.info(f"Database already populated: {existing_stages} stages, {existing_tools} tools - skipping initialization")
        return
    
    logger.info("Database needs initialization - proceeding with data setup...")
    
    # Deactivate any existing auto-created tools to prevent conflicts
    auto_tools = ExemplarTool.query.filter_by(auto_created=True, is_active=True).all()
    for tool in auto_tools:
        tool.is_active = False
    logger.info(f"Deactivated {len(auto_tools)} existing auto-created tools")
    
    # MaLDReTH 1.0 reference data (simplified for reliability)
    maldreth_data = {
        "CONCEPTUALISE": {
            "description": "To formulate the initial research idea or hypothesis, and define the scope of the research project and data requirements.",
            "categories": {
                "Mind mapping, concept mapping and knowledge modelling": ["FreeMind", "XMind", "Lucidchart", "Miro", "Roam Research"],
                "Diagramming and flowchart": ["Draw.io", "Visio", "Creately"],
                "Literature review": ["Zotero", "Mendeley"]
            }
        },
        "PLAN": {
            "description": "To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resource allocation.",
            "categories": {
                "Data management planning (DMP)": ["DMPTool", "DMP Assistant", "DMPT"],
                "Project planning": ["Gantt Project", "Microsoft Project", "Trello"],
                "Research methodology": ["NVivo", "Atlas.ti"]
            }
        },
        "FUND": {
            "description": "To identify and acquire financial resources to support the research project, including data collection, analysis, storage, and dissemination activities.",
            "categories": {}  # No specific tools for funding stage
        },
        "COLLECT": {
            "description": "To gather primary and secondary data according to the research methodology and ethical guidelines established during the planning phase.",
            "categories": {
                "Survey and questionnaire": ["SurveyMonkey", "Google Forms", "Qualtrics"],
                "Data collection": ["ODK", "KoBoToolbox", "REDCap"],
                "Field data collection": ["Epicollect5", "Survey123", "Fulcrum"]
            }
        },
        "PROCESS": {
            "description": "To transform, clean, validate, and prepare raw data for analysis, ensuring data quality and consistency.",
            "categories": {
                "Electronic Laboratory Notebooks (ELNs)": ["LabArchives", "eLabJournal"],
                "Scientific computing across all programming languages": ["Jupyter", "RStudio"],
                "Data cleaning and transformation": ["OpenRefine", "Trifacta", "DataLadder"]
            }
        },
        "ANALYSE": {
            "description": "To examine, interpret, and derive insights from processed data using appropriate analytical methods and tools.",
            "categories": {
                "Statistical analysis": ["R", "SPSS", "SAS"],
                "Data visualization": ["Tableau", "D3.js"],
                "Machine learning": ["Python scikit-learn", "TensorFlow"]
            }
        },
        "STORE": {
            "description": "To securely store processed data and analysis results in appropriate formats and locations for future access and use.",
            "categories": {
                "Data repository": ["Figshare", "Zenodo"],
                "Archive": ["DSpace"],
                "Cloud storage": ["Google Drive", "Dropbox", "OneDrive"]
            }
        },
        "PUBLISH": {
            "description": "To share research findings and datasets through appropriate channels, ensuring proper attribution and accessibility.",
            "categories": {
                "Academic publishing": ["LaTeX", "Overleaf", "Word"],
                "Data publication": ["Dataverse", "Figshare"],
                "Preprint servers": ["arXiv", "bioRxiv", "PeerJ Preprints"]
            }
        },
        "PRESERVE": {
            "description": "To ensure long-term accessibility and integrity of research data and outputs through appropriate preservation strategies.",
            "categories": {
                "Digital preservation": ["LOCKSS", "Fedora", "DSpace", "Samvera"],
                "Data repository": ["Institutional Repository", "Domain Repository", "Zenodo", "Figshare"],
                "Archive": ["Digital preservation system"]
            }
        },
        "SHARE": {
            "description": "To make research data and findings available to other researchers and stakeholders through appropriate sharing mechanisms.",
            "categories": {
                "Data repository": ["GitHub", "Zenodo"],
                "Electronic Laboratory Notebooks (ELNs)": ["LabArchives", "Benchling", "eLabNext", "Lab Archives"],
                "Scientific computing across all programming languages": ["Jupyter", "Eclipse", "Jupyter"]
            }
        },
        "ACCESS": {
            "description": "To provide controlled and documented access to research data for verification, reuse, and further research activities.",
            "categories": {
                "Data repository": ["DataCite", "CKAN"],
                "Access control": ["Shibboleth", "OAuth"],
                "Data discovery": ["DataCite", "Google Dataset Search", "CKAN"]
            }
        },
        "TRANSFORM": {
            "description": "To convert and adapt research data and outputs into new formats, applications, or research contexts.",
            "categories": {
                "Data transformation": ["Apache Spark", "Talend", "Pentaho"],
                "Electronic Laboratory Notebooks (ELNs)": ["LabArchives"],
                "Format conversion": ["Pandoc", "ImageMagick", "FFmpeg"]
            }
        }
    }
    
    # Create or update stages and categories
    for position, (stage_name, stage_info) in enumerate(maldreth_data.items()):
        # Get or create stage
        stage = MaldrethStage.query.filter_by(name=stage_name).first()
        if not stage:
            stage = MaldrethStage(
                name=stage_name,
                description=stage_info["description"],
                position=position
            )
            db.session.add(stage)
            db.session.flush()  # Get the stage ID
        
        # Create categories and tools for this stage
        for category_name, tools in stage_info["categories"].items():
            # Get or create category
            category = ToolCategory.query.filter_by(
                name=category_name, 
                stage_id=stage.id
            ).first()
            
            if not category:
                category = ToolCategory(
                    name=category_name,
                    stage_id=stage.id,
                    description=f"Category for {category_name} tools in {stage_name} stage"
                )
                db.session.add(category)
                db.session.flush()  # Get the category ID
            
            # Add tools to this category (prevent duplicates)
            for tool_name in tools:
                # Check if tool already exists in this category
                existing_tool = ExemplarTool.query.filter_by(
                    name=tool_name,
                    category_id=category.id,
                    stage_id=stage.id,
                    is_active=True
                ).first()
                
                if not existing_tool:
                    tool = ExemplarTool(
                        name=tool_name,
                        stage_id=stage.id,
                        category_id=category.id,
                        description=f"{tool_name} - {category_name} tool for {stage_name}",
                        is_active=True,
                        auto_created=True,
                        import_source="MaLDReTH 1.0 Initial Data"
                    )
                    db.session.add(tool)
    
    # Commit all changes
    db.session.commit()
    
    # Final statistics
    total_stages = MaldrethStage.query.count()
    total_categories = ToolCategory.query.count()
    total_active_tools = ExemplarTool.query.filter_by(is_active=True).count()
    
    logger.info(f"Database initialization complete:")
    logger.info(f"  Stages: {total_stages}")
    logger.info(f"  Categories: {total_categories}")  
    logger.info(f"  Active tools: {total_active_tools}")

@app.route('/d3-diagnostic')
def d3_diagnostic():
    """Diagnostic page for D3.js issues."""
    return render_template('d3_diagnostic.html')


if __name__ == '__main__':
    with app.app_context():
        # Run database migrations for new fields
        migrate_database_schema()
        
        # This will re-create the database each time the app starts.
        # For a real deployment, you'd use migrations instead.
        init_database_with_maldreth_data()
    
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
