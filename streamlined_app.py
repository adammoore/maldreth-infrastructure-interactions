"""
streamlined_app.py
Refactored Flask application for MaLDReTH tool interaction capture.

This version aligns with the MaLDReTH 1.0 final outputs, including:
1. The 12 harmonised Research Data Lifecycle (RDL) stages.
2. A comprehensive list of tool categories and exemplar tools.
3. A detailed interaction capture form based on the project's Google Sheet.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Data Models ---

class MaldrethStage(db.Model):
    """Model representing the 12 stages in the MaLDReTH RDL."""
    __tablename__ = 'maldreth_stages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, default=0)
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
    stage_id = db.Column(db.Integer, db.ForeignKey('maldreth_stages.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=False)
    source_interactions = db.relationship('ToolInteraction', foreign_keys='ToolInteraction.source_tool_id', backref='source_tool', lazy='dynamic')
    target_interactions = db.relationship('ToolInteraction', foreign_keys='ToolInteraction.target_tool_id', backref='target_tool', lazy='dynamic')

class ToolInteraction(db.Model):
    """Model representing interactions between tools, aligned with the Google Sheet fields."""
    __tablename__ = 'tool_interactions'
    id = db.Column(db.Integer, primary_key=True)
    source_tool_id = db.Column(db.Integer, db.ForeignKey('exemplar_tools.id'), nullable=False)
    target_tool_id = db.Column(db.Integer, db.ForeignKey('exemplar_tools.id'), nullable=False)
    interaction_type = db.Column(db.String(100), nullable=False)
    lifecycle_stage = db.Column(db.String(50), nullable=False)
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
    """Add a new tool interaction."""
    stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
    tools = ExemplarTool.query.order_by(ExemplarTool.name).all()
    
    if request.method == 'POST':
        try:
            interaction = ToolInteraction(
                source_tool_id=int(request.form.get('source_tool_id')),
                target_tool_id=int(request.form.get('target_tool_id')),
                interaction_type=request.form.get('interaction_type'),
                lifecycle_stage=request.form.get('lifecycle_stage'),
                description=request.form.get('description'),
                technical_details=request.form.get('technical_details'),
                benefits=request.form.get('benefits'),
                challenges=request.form.get('challenges'),
                examples=request.form.get('examples'),
                contact_person=request.form.get('contact_person'),
                organization=request.form.get('organization'),
                email=request.form.get('email'),
                priority=request.form.get('priority'),
                complexity=request.form.get('complexity'),
                status=request.form.get('status'),
                submitted_by=request.form.get('submitted_by')
            )
            db.session.add(interaction)
            db.session.commit()
            flash('Interaction added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error adding interaction: {e}")
            db.session.rollback()
            flash('Error adding interaction. Please try again.', 'error')

    return render_template('streamlined_add_interaction.html', tools=tools, stages=stages)

@app.route('/interactions')
def view_interactions():
    """View all interactions."""
    try:
        interactions = ToolInteraction.query.order_by(ToolInteraction.submitted_at.desc()).all()
        return render_template('streamlined_view_interactions.html', interactions=interactions)
    except Exception as e:
        logger.error(f"Error viewing interactions: {e}")
        return render_template('error.html', error=str(e)), 500

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

def init_database_with_maldreth_data():
    """Clear and initialize the database with MaLDReTH 1.0 final output data."""
    try:
        # Drop all tables with cascade
        db.session.execute(db.text('DROP TABLE IF EXISTS tool_interactions CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS exemplar_tools CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS tool_categories CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS maldreth_stages CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS research_tools CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS tools CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS interactions CASCADE'))
        db.session.commit()
    except Exception as e:
        logger.info(f"Tables may not exist yet: {e}")
        db.session.rollback()
    
    db.create_all()

    # 1. Create RDL Stages
    stages_data = [
        ("CONCEPTUALISE", "To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.", 0),
        ("PLAN", "To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis.", 1),
        ("FUND", "To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.", 2),
        ("COLLECT", "To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.", 3),
        ("PROCESS", "To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.", 4),
        ("ANALYSE", "To derive insights, knowledge, and understanding from processed data.", 5),
        ("STORE", "To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.", 6),
        ("PUBLISH", "To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.", 7),
        ("PRESERVE", "To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.", 8),
        ("SHARE", "To make data available and accessible to humans and/or machines.", 9),
        ("ACCESS", "To control and manage data access by designated users and reusers.", 10),
        ("TRANSFORM", "To create new data from the original, for example by migration into a different format or by creating a subset.", 11)
    ]
    for name, desc, pos in stages_data:
        stage = MaldrethStage(name=name, description=desc, position=pos)
        db.session.add(stage)
    db.session.commit()

    # 2. Create Tool Categories and Tools
    tools_catalog = {
        "CONCEPTUALISE": [
            ("Mind mapping, concept mapping and knowledge modelling", "Tools that define the entities of research and their relationships", ["Miro", "Meister Labs (MindMeister + MeisterTask)", "XMind"]),
            ("Diagramming and flowchart", "Tools that detail the research workflow", ["Lucidchart", "Draw.io (now Diagrams.net)", "Creately"]),
            ("Wireframing and prototyping", "Tools that visualise and demonstrate the research workflow", ["Balsamiq", "(Figma)"])
        ],
        "PLAN": [
            ("Data management planning (DMP)", "Tools focused on enabling preparation and submission of data management plans", ["DMP Tool", "DMP Online", "RDMO"]),
            ("Project planning", "Tools designed to enable project planning", ["Trello", "Asana", "Microsoft project"]),
            ("Combined DMP/project", "Tools which combine project planning with the ability to prepare data management plans", ["Data Stewardship Wizard", "Redbox research data", "Argos"])
        ],
        "COLLECT": [
            ("Quantitative data collection tool", "Tools that collect quantitative data", ["Open Data Kit", "GBIF", "Cedar WorkBench"]),
            ("Qualitative data collection (e.g. Survey tool)", "Tools that collect qualitative data", ["Survey Monkey", "Online Surveys", "Zooniverse"]),
            ("Harvesting tool (e.g. WebScrapers)", "Tools that harvest data from various sources", ["Netlytic", "IRODS", "DROID"])
        ],
        "PROCESS": [
            ("Electronic laboratory notebooks (ELNs)", "Tools that enable aggregation, management, and organization of experimental and physical sample data", ["elabnext", "E-lab FTW (Open source)", "RSpace (Open Source)", "Lab Archives"]),
            ("Scientific computing across all programming languages", "Tools that enable creation and sharing of computational documents", ["Jupyter", "Mathematica", "WebAssembly"]),
            ("Metadata Tool", "Tools that enable creation, application, and management of metadata", ["CEDAR Workbench (biomedical data)"])
        ],
        "ANALYSE": [
            ("Remediation (e.g. motion capture for gait analysis)", "Tools that capture transformation of data observations", ["Track3D"]),
            ("Computational methods (e.g. Statistical software)", "Tools that provide computational methods for analysis", ["SPSS", "Matlab"]),
            ("Computational tools", "Tools that provide computational frameworks for processing and analysis", ["Jupyter", "RStudio", "Eclipse"])
        ],
        "STORE": [
            ("Data Repository", "Tools that structure and provide a framework to organise information", ["Figshare", "Zenodo", "Dataverse"]),
            ("Archive", "Tools that facilitate the long-term storage of data", ["Libsafe"]),
            ("Management tool", "Tools that facilitate the organisation of data", ["iRODS", "GLOBUS", "Mediaflux"])
        ],
        "PUBLISH": [
            ("Discipline-specific data repository", "Tools that enable storage and public sharing of data for specific disciplines", ["NOMAD-OASIS"]),
            ("Generalist data repository", "Tools that enable storage and public sharing of generalist data", ["Figshare", "Zenodo", "Dataverse", "CKAN"]),
            ("Metadata repository", "Tools that enable the storage and public sharing of metadata", ["DataCite Commons", "IBM Infosphere"])
        ],
        "PRESERVE": [
            ("Data repository", "Tools that enable storage and public sharing of data", ["Dataverse", "Invenio UKDS"]),
            ("Archive", "Tools that facilitate the long-term preservation of data", ["Archivematica"]),
            ("Containers", "Tools that create an environment in which data can be seen in its original environment", ["Preservica", "Docker", "Archive-it.org"])
        ],
        "SHARE": [
            ("Data repository", "Tools that enable storage and public sharing of data", ["Dataverse", "Zenodo", "Figshare"]),
            ("Electronic laboratory notebooks (ELNs)", "Tools that enable aggregation, organization and management of experimental and physical sample data", ["elabftw", "RSpace", "elabnext", "lab archives"]),
            ("Scientific computing across all programming languages", "Tools that enable creation and sharing of computational documents", ["Eclipse", "Jupyter", "Wolfram Alpha"])
        ],
        "ACCESS": [
            ("Data repository", "Tools that store data so that it can be publicly accessed", ["CKAN", "Dataverse", "DRYAD"]),
            ("Database", "Tools that structure and provide a framework to access information", ["Oracle", "MySQL / sqlLite", "Postgres"]),
            ("Authorisation/Authentication Infrastructure", "Tools that enable scalable authorised and authenticated access to data", ["LDAP", "SAML2", "AD"])
        ],
        "TRANSFORM": [
            ("Electronic laboratory notebooks (ELNs)", "Tools that enable aggregation, management, and organization of experimental and physical sample data", ["elabftw", "RSpace", "elabnext", "Lab archive"]),
            ("Programming languages", "Tools and platforms infrastructure used to transform data", ["Python (Interpreted language)", "Perl (4GL)", "Fortran (Compiled language)"]),
            ("Extract, Transform, Load (ETL) tools", "A data integration process used to combine data from multiple sources", ["OCI (Cloud Infrastructure Provider)", "Apache Spark", "Snowflake (Commercial)"])
        ]
    }

    for stage_name, categories in tools_catalog.items():
        stage_obj = MaldrethStage.query.filter_by(name=stage_name).one()
        for cat_name, cat_desc, tools in categories:
            category_obj = ToolCategory(name=cat_name, description=cat_desc, stage_id=stage_obj.id)
            db.session.add(category_obj)
            db.session.flush() # Get category ID
            for tool_name in tools:
                tool_obj = ExemplarTool(name=tool_name, stage_id=stage_obj.id, category_id=category_obj.id)
                db.session.add(tool_obj)

    db.session.commit()
    logger.info("Database initialized with MaLDReTH 1.0 data.")


if __name__ == '__main__':
    with app.app_context():
        # This will re-create the database each time the app starts.
        # For a real deployment, you'd use migrations instead.
        init_database_with_maldreth_data()
    
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
