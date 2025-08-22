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
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    stage_id = db.Column(db.Integer, db.ForeignKey('maldreth_stages.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_open_source = db.Column(db.Boolean, default=False)
    provider = db.Column(db.String(200))  # MaLDReTH compatibility: tool provider/organization
    auto_created = db.Column(db.Boolean, default=False)  # Track if created from CSV import
    import_source = db.Column(db.String(100))  # Track origin of tool data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
    """Add a new tool interaction."""
    stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
    tools = ExemplarTool.query.order_by(ExemplarTool.name).all()
    interaction_types = INTERACTION_TYPES
    lifecycle_stages = LIFECYCLE_STAGES
    
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

    return render_template('streamlined_add_interaction.html', 
                         tools=tools, 
                         stages=stages, 
                         interaction_types=interaction_types, 
                         lifecycle_stages=lifecycle_stages)

@app.route('/interactions')
def view_interactions():
    """View all interactions."""
    try:
        interactions = ToolInteraction.query.order_by(ToolInteraction.submitted_at.desc()).all()
        return render_template('streamlined_view_interactions.html', interactions=interactions)
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
            interaction.lifecycle_stage = request.form.get('lifecycle_stage')
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
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        interaction_types = INTERACTION_TYPES
        lifecycle_stages = [stage.name for stage in stages]
        
        return render_template('streamlined_edit_interaction.html', 
                             interaction=interaction,
                             tools=tools, 
                             stages=stages, 
                             interaction_types=interaction_types, 
                             lifecycle_stages=lifecycle_stages)
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
                    submitted_at=datetime.now()
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

@app.route('/about')
def about():
    """About page with MaLDReTH II and RDA context."""
    return render_template('about.html')

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
        
        # Get tool usage in interactions
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
        
        # Get recent interactions
        recent_interactions = ToolInteraction.query.order_by(
            ToolInteraction.submitted_at.desc()
        ).limit(5).all()
        
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
                             stages=stages, 
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
        
        # Simple stage data with tool counts
        for stage in stages:
            stage_tools = [t for t in tools if t.stage_id == stage.id]
            stage_data = {
                'id': stage.id,
                'tool_count': len(stage_tools)
            }
            visualization_data['stages'].append(stage_data)
        
        return render_template('simple_maldreth_visualization.html',
                             stages=stages,
                             visualization_data=visualization_data)
                             
    except Exception as e:
        logger.error(f"Error in simple MaLDReTH visualization: {e}")
        return render_template('error.html', error=str(e)), 500

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
            logger.info("exemplar_tools table doesn't exist, will be created")
            return
            
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
