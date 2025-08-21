"""
app_unified.py
Unified Flask Application for MaLDReTH Tool Interaction Capture System.

This module provides the main Flask application with integrated functionality from:
- Original MaLDReTH lifecycle visualization
- Streamlined tool interaction capture  
- Community feedback and analytics
- API endpoints for data access

For LLM/Copilot Understanding:
This is the main application entry point that:
1. Initializes the Flask app with proper configuration
2. Sets up database connections and extensions
3. Registers all route blueprints (main app + interactions)
4. Configures error handling and logging
5. Provides database initialization functionality

Key Integration Points:
- Uses unified models from models.py
- Combines routes from both original and streamlined versions
- Maintains backward compatibility while adding new features
- Supports both factory pattern and direct instantiation
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
from typing import Optional

# Import extensions and configuration
from extensions import db, migrate
from config import Config

# Import models - using unified model structure
from models import (
    MaldrethStage, ExemplarTool, ToolCategory, ToolInteraction, 
    Connection, UserInteraction, SiteInteraction,
    get_stage_by_name, get_tools_by_stage, get_tool_interactions
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def create_app(config_class=Config) -> Flask:
    """
    Create and configure the unified MaLDReTH Flask application.
    
    This function implements the application factory pattern and integrates
    all functionality from both the original application and streamlined
    interaction capture system.
    
    For LLM/Copilot: This is the primary function for creating the app instance.
    It handles all initialization, configuration, and setup. Use this for
    both development and production deployments.
    
    Args:
        config_class: Configuration class to use (default: Config)
        
    Returns:
        Flask: Fully configured Flask application instance
        
    Raises:
        Exception: If application creation fails
    """
    try:
        # Create Flask instance with template and static folder configuration
        app = Flask(__name__,
                   template_folder='templates',
                   static_folder='static')
        
        # Load configuration from config class
        app.config.from_object(config_class)
        logger.info(f"Application configured for {config_class.__name__} environment")
        
        # Initialize database and migration extensions
        # For LLM/Copilot: db provides SQLAlchemy ORM, migrate handles schema changes
        db.init_app(app)
        migrate.init_app(app, db)
        logger.info("Database extensions initialized successfully")
        
        # Initialize CORS for API access
        # For LLM/Copilot: This enables cross-origin requests for API endpoints
        CORS(app, resources={
            r"/api/*": {"origins": "*"},  # API endpoints open to all origins
            r"/export/*": {"origins": "*"}  # Export endpoints for data download
        })
        logger.info("CORS configured for API access")
        
        # Register all application routes and blueprints within app context
        with app.app_context():
            # Register main application routes (unified from routes.py and streamlined_app.py)
            register_unified_routes(app)
            logger.info("Unified routes registered successfully")
            
            # Create database tables if they don't exist
            # For LLM/Copilot: This ensures all models are reflected in the database
            db.create_all()
            logger.info("Database tables created successfully")
        
        # Register comprehensive error handlers
        register_error_handlers(app)
        logger.info("Error handlers registered successfully")
        
        logger.info("Unified MaLDReTH Flask application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Flask application: {e}")
        raise


def register_unified_routes(app: Flask) -> None:
    """
    Register all unified routes combining original and streamlined functionality.
    
    This function consolidates routes from:
    - Original MaLDReTH application (lifecycle visualization)
    - Streamlined interaction capture system
    - API endpoints for data access
    - Administrative and utility functions
    
    For LLM/Copilot: This replaces the blueprint registration pattern with
    direct route registration to avoid circular imports and ensure proper
    integration of all functionality.
    
    Args:
        app: Flask application instance to register routes on
    """
    
    # ===== MAIN APPLICATION ROUTES =====
    
    @app.route('/')
    def index():
        """
        Main landing page displaying MaLDReTH lifecycle overview with statistics.
        
        Combines functionality from both original and streamlined applications:
        - Shows the 12 RDL stages in visual format
        - Displays interaction statistics and recent activity
        - Provides navigation to detailed views
        
        For LLM/Copilot: This is the primary entry point for users.
        """
        try:
            # Get all stages ordered by position for lifecycle display
            stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
            
            # Calculate summary statistics for dashboard
            total_interactions = ToolInteraction.query.count()
            total_tools = ExemplarTool.query.filter_by(is_active=True).count()
            total_stages = len(stages)
            
            # Get recent interactions for activity feed
            recent_interactions = ToolInteraction.query.order_by(
                ToolInteraction.submitted_at.desc()
            ).limit(5).all()
            
            # Get stage connections for visualization
            connections = Connection.query.all()
            
            return render_template('index.html',
                                 stages=stages,
                                 connections=connections,
                                 total_interactions=total_interactions,
                                 total_tools=total_tools,
                                 total_stages=total_stages,
                                 recent_interactions=recent_interactions)
        except Exception as e:
            logger.error(f"Error in index route: {e}")
            return render_template('error.html', error=str(e)), 500
    
    @app.route('/stage/<stage_name>')
    def stage_detail(stage_name: str):
        """
        Display detailed information about a specific MaLDReTH stage.
        
        Shows:
        - Stage description and position in lifecycle
        - All tool categories within the stage
        - All exemplar tools with interaction counts
        - Related interactions and workflows
        
        For LLM/Copilot: Use this to explore stage-specific tools and integrations.
        
        Args:
            stage_name: Name of the MaLDReTH stage (e.g., 'CONCEPTUALISE')
        """
        try:
            stage = get_stage_by_name(stage_name)
            if not stage:
                flash(f"Stage '{stage_name}' not found", 'error')
                return redirect(url_for('index'))
            
            # Get organized data for the stage
            tool_categories = stage.tool_categories.all()
            tools = stage.tools.filter_by(is_active=True).all()
            
            # Get interactions involving tools from this stage
            stage_interactions = []
            for tool in tools:
                stage_interactions.extend(get_tool_interactions(tool.id))
            
            return render_template('stage_detail.html',
                                 stage=stage,
                                 tool_categories=tool_categories,
                                 tools=tools,
                                 interactions=stage_interactions[:10])  # Limit for performance
        except Exception as e:
            logger.error(f"Error displaying stage detail: {e}")
            flash("Error loading stage information", 'error')
            return redirect(url_for('index'))
    
    # ===== TOOL INTERACTION ROUTES =====
    
    @app.route('/add-interaction', methods=['GET', 'POST'])
    def add_interaction():
        """
        Handle tool interaction creation (from streamlined app).
        
        GET: Display the interaction creation form with tool selection
        POST: Process form submission and create new ToolInteraction record
        
        For LLM/Copilot: This is how users contribute new tool interaction data.
        Form includes all fields from the Google Sheet specification.
        """
        # Get reference data for form dropdowns
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
        tools = ExemplarTool.query.filter_by(is_active=True).order_by(ExemplarTool.name).all()
        
        if request.method == 'POST':
            try:
                # Extract form data with validation
                source_tool_id = request.form.get('source_tool_id')
                target_tool_id = request.form.get('target_tool_id')
                
                if not source_tool_id or not target_tool_id:
                    flash('Both source and target tools are required', 'error')
                    return render_template('add_interaction.html', tools=tools, stages=stages)
                
                # Create new interaction record with comprehensive data
                interaction = ToolInteraction(
                    source_tool_id=int(source_tool_id),
                    target_tool_id=int(target_tool_id),
                    interaction_type=request.form.get('interaction_type', 'data_flow'),
                    lifecycle_stage=request.form.get('lifecycle_stage', ''),
                    description=request.form.get('description', ''),
                    technical_details=request.form.get('technical_details', ''),
                    benefits=request.form.get('benefits', ''),
                    challenges=request.form.get('challenges', ''),
                    examples=request.form.get('examples', ''),
                    contact_person=request.form.get('contact_person', ''),
                    organization=request.form.get('organization', ''),
                    email=request.form.get('email', ''),
                    priority=request.form.get('priority', 'medium'),
                    complexity=request.form.get('complexity', 'medium'),
                    status=request.form.get('status', 'active'),
                    submitted_by=request.form.get('submitted_by', '')
                )
                
                db.session.add(interaction)
                db.session.commit()
                
                flash('Tool interaction added successfully!', 'success')
                logger.info(f"New interaction created: {interaction.source_tool.name} -> {interaction.target_tool.name}")
                return redirect(url_for('view_interactions'))
                
            except Exception as e:
                logger.error(f"Error adding interaction: {e}")
                db.session.rollback()
                flash('Error adding interaction. Please try again.', 'error')
        
        return render_template('add_interaction.html', tools=tools, stages=stages)
    
    @app.route('/interactions')
    def view_interactions():
        """
        Display all tool interactions with filtering and sorting options.
        
        Shows paginated list of interactions with:
        - Source and target tool information
        - Interaction type and stage
        - Status and complexity indicators
        - Links to detailed views
        
        For LLM/Copilot: This provides the main interface for browsing
        all captured tool interactions.
        """
        try:
            # Get filter parameters from query string
            stage_filter = request.args.get('stage')
            type_filter = request.args.get('type')
            status_filter = request.args.get('status')
            
            # Build query with optional filters
            query = ToolInteraction.query
            
            if stage_filter:
                query = query.filter(ToolInteraction.lifecycle_stage == stage_filter)
            if type_filter:
                query = query.filter(ToolInteraction.interaction_type == type_filter)
            if status_filter:
                query = query.filter(ToolInteraction.status == status_filter)
            
            # Order by most recent first
            interactions = query.order_by(ToolInteraction.submitted_at.desc()).all()
            
            # Get filter options for form dropdowns
            stages = MaldrethStage.query.all()
            interaction_types = db.session.query(ToolInteraction.interaction_type).distinct().all()
            statuses = db.session.query(ToolInteraction.status).distinct().all()
            
            return render_template('view_interactions.html',
                                 interactions=interactions,
                                 stages=stages,
                                 interaction_types=[t[0] for t in interaction_types if t[0]],
                                 statuses=[s[0] for s in statuses if s[0]],
                                 current_filters={
                                     'stage': stage_filter,
                                     'type': type_filter,
                                     'status': status_filter
                                 })
        except Exception as e:
            logger.error(f"Error viewing interactions: {e}")
            return render_template('error.html', error=str(e)), 500
    
    @app.route('/interaction/<int:interaction_id>')
    def interaction_detail(interaction_id: int):
        """
        Display detailed view of a specific tool interaction.
        
        Shows complete interaction data including:
        - Technical implementation details
        - Benefits and challenges
        - Contact information and examples
        - Related interactions with same tools
        
        For LLM/Copilot: This provides the full context for understanding
        how specific tool integrations work.
        
        Args:
            interaction_id: Database ID of the ToolInteraction record
        """
        try:
            interaction = ToolInteraction.query.get_or_404(interaction_id)
            
            # Find related interactions (same tools, different directions/types)
            related_interactions = ToolInteraction.query.filter(
                db.and_(
                    ToolInteraction.id != interaction_id,
                    db.or_(
                        db.and_(
                            ToolInteraction.source_tool_id.in_([interaction.source_tool_id, interaction.target_tool_id]),
                            ToolInteraction.target_tool_id.in_([interaction.source_tool_id, interaction.target_tool_id])
                        )
                    )
                )
            ).limit(5).all()
            
            return render_template('interaction_detail.html',
                                 interaction=interaction,
                                 related_interactions=related_interactions)
        except Exception as e:
            logger.error(f"Error viewing interaction detail: {e}")
            return render_template('error.html', error=str(e)), 500
    
    # ===== USER FEEDBACK ROUTES =====
    
    @app.route('/submit-feedback', methods=['POST'])
    def submit_feedback():
        """
        Handle user feedback submission for community contributions.
        
        Processes feedback forms and creates UserInteraction records.
        Supports both AJAX and traditional form submissions.
        
        For LLM/Copilot: This captures valuable community knowledge
        about tool usage, missing integrations, and improvements.
        """
        try:
            # Extract and validate form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            organization = request.form.get('organization', '').strip()
            role = request.form.get('role', '').strip()
            feedback = request.form.get('feedback', '').strip()
            
            # Basic validation
            if not name or not email:
                if request.is_json:
                    return jsonify({'error': 'Name and email are required'}), 400
                flash('Name and email are required', 'error')
                return redirect(url_for('index'))
            
            # Create user feedback record
            user_interaction = UserInteraction(
                name=name,
                email=email,
                organization=organization,
                role=role,
                feedback=feedback
            )
            
            db.session.add(user_interaction)
            db.session.commit()
            
            logger.info(f"User feedback recorded: {email} from {organization}")
            
            if request.is_json:
                return jsonify({'message': 'Thank you for your feedback!'}), 200
            
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': 'Database error'}), 500
            flash('Error submitting feedback. Please try again.', 'error')
            return redirect(url_for('index'))
    
    # ===== API ENDPOINTS =====
    
    @app.route('/api/stages')
    def api_stages():
        """
        API endpoint to retrieve all MaLDReTH stages with metadata.
        
        Returns JSON array of stage objects including:
        - Basic stage information (id, name, description, position)
        - Tool and category counts
        - Color coding for visualization
        
        For LLM/Copilot: Use this to build dynamic interfaces or
        integrate with other systems.
        """
        try:
            stages = MaldrethStage.query.order_by(MaldrethStage.position).all()
            return jsonify([{
                **stage.to_dict(),
                'tool_count': stage.get_tool_count(),
                'category_count': stage.get_category_count()
            } for stage in stages])
        except Exception as e:
            logger.error(f"API error getting stages: {e}")
            return jsonify({'error': 'Error retrieving stages'}), 500
    
    @app.route('/api/tools/<stage_name>')
    def api_tools_by_stage(stage_name: str):
        """
        API endpoint to retrieve all tools for a specific stage.
        
        Args:
            stage_name: Name of the MaLDReTH stage
            
        Returns:
            JSON array of tool objects with interaction counts
        """
        try:
            tools = get_tools_by_stage(stage_name)
            return jsonify([{
                **tool.to_dict(),
                'connected_tool_count': len(tool.get_connected_tools())
            } for tool in tools])
        except Exception as e:
            logger.error(f"API error getting tools for stage {stage_name}: {e}")
            return jsonify({'error': 'Error retrieving tools'}), 500
    
    @app.route('/api/interactions')
    def api_interactions():
        """
        API endpoint to retrieve tool interactions with optional filtering.
        
        Query parameters:
        - stage: Filter by lifecycle stage
        - type: Filter by interaction type
        - status: Filter by interaction status
        - limit: Maximum number of results (default: 100)
        
        For LLM/Copilot: Use this to build custom interfaces or
        analyze interaction patterns programmatically.
        """
        try:
            # Get filter parameters
            stage_filter = request.args.get('stage')
            type_filter = request.args.get('type')
            status_filter = request.args.get('status')
            limit = int(request.args.get('limit', 100))
            
            # Build filtered query
            query = ToolInteraction.query
            if stage_filter:
                query = query.filter(ToolInteraction.lifecycle_stage == stage_filter)
            if type_filter:
                query = query.filter(ToolInteraction.interaction_type == type_filter)
            if status_filter:
                query = query.filter(ToolInteraction.status == status_filter)
            
            interactions = query.order_by(
                ToolInteraction.submitted_at.desc()
            ).limit(limit).all()
            
            return jsonify([interaction.to_dict() for interaction in interactions])
        except Exception as e:
            logger.error(f"API error getting interactions: {e}")
            return jsonify({'error': 'Error retrieving interactions'}), 500
    
    # ===== DATA EXPORT ROUTES =====
    
    @app.route('/export/csv')
    def export_interactions_csv():
        """
        Export all tool interactions to CSV format for external analysis.
        
        Generates a comprehensive CSV file with all interaction fields
        suitable for spreadsheet analysis or data processing.
        
        For LLM/Copilot: This enables users to work with interaction data
        in external tools like Excel, R, or Python for analysis.
        """
        try:
            import csv
            from io import StringIO
            from flask import make_response
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write comprehensive header row
            writer.writerow([
                'ID', 'Source Tool', 'Source Stage', 'Target Tool', 'Target Stage',
                'Interaction Type', 'Lifecycle Stage', 'Description', 'Technical Details',
                'Benefits', 'Challenges', 'Examples', 'Contact Person', 'Organization',
                'Email', 'Priority', 'Complexity', 'Status', 'Submitted By', 'Submitted At'
            ])
            
            # Write interaction data
            interactions = ToolInteraction.query.all()
            for interaction in interactions:
                writer.writerow([
                    interaction.id,
                    interaction.source_tool.name if interaction.source_tool else '',
                    interaction.source_tool.stage.name if interaction.source_tool and interaction.source_tool.stage else '',
                    interaction.target_tool.name if interaction.target_tool else '',
                    interaction.target_tool.stage.name if interaction.target_tool and interaction.target_tool.stage else '',
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
            response.headers['Content-Disposition'] = f'attachment; filename=maldreth_interactions_{datetime.now().strftime("%Y%m%d")}.csv'
            return response
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            flash('Error exporting data. Please try again.', 'error')
            return redirect(url_for('index'))


def register_error_handlers(app: Flask) -> None:
    """
    Register comprehensive error handlers for the application.
    
    Provides user-friendly error pages and proper logging for debugging.
    Handles both HTML and JSON responses based on request type.
    
    For LLM/Copilot: These handlers ensure graceful error handling
    and provide useful information for debugging issues.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors with context-aware responses."""
        logger.warning(f"404 error: {error} - URL: {request.url}")
        
        if request.is_json:
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('error.html', 
                             error="Page not found",
                             error_code=404,
                             suggestion="Check the URL or return to the homepage"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors with database rollback."""
        logger.error(f"500 error: {error} - URL: {request.url}")
        db.session.rollback()  # Ensure database consistency
        
        if request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('error.html',
                             error="Internal server error",
                             error_code=500,
                             suggestion="Please try again or contact support if the problem persists"), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors for malformed requests."""
        logger.warning(f"400 error: {error} - URL: {request.url}")
        
        if request.is_json:
            return jsonify({'error': 'Bad request'}), 400
        return render_template('error.html',
                             error="Bad request",
                             error_code=400,
                             suggestion="Check your input and try again"), 400
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all other unhandled exceptions with full logging."""
        logger.error(f"Unhandled exception: {error} - URL: {request.url}", exc_info=True)
        db.session.rollback()
        
        if request.is_json:
            return jsonify({'error': 'An unexpected error occurred'}), 500
        return render_template('error.html',
                             error=str(error),
                             error_code=500,
                             suggestion="An unexpected error occurred. Please try again."), 500


def init_database_with_maldreth_data(app: Optional[Flask] = None) -> None:
    """
    Initialize database with comprehensive MaLDReTH 1.0 data.
    
    This function creates and populates the database with:
    - 12 harmonized Research Data Lifecycle stages
    - Tool categories and exemplar tools from MaLDReTH outputs
    - Stage connections for lifecycle visualization
    
    For LLM/Copilot: This function sets up the complete data foundation.
    Run this once to populate the database with the official MaLDReTH taxonomy.
    
    Args:
        app: Flask application instance (uses current app context if None)
    """
    if app:
        with app.app_context():
            _populate_maldreth_data()
    else:
        _populate_maldreth_data()


def _populate_maldreth_data() -> None:
    """
    Internal function to populate database with MaLDReTH reference data.
    
    For LLM/Copilot: This contains the authoritative data from MaLDReTH 1.0
    final outputs. Do not modify without careful consideration of impacts.
    """
    try:
        # Clear existing data if reinitializing
        logger.info("Clearing existing data for reinitialization...")
        ToolInteraction.query.delete()
        ExemplarTool.query.delete()
        ToolCategory.query.delete()
        Connection.query.delete()
        MaldrethStage.query.delete()
        db.session.commit()
        
        # Create the 12 MaLDReTH RDL stages with official descriptions
        stages_data = [
            ("CONCEPTUALISE", "To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.", 0, "#FF6B6B"),
            ("PLAN", "To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis.", 1, "#4ECDC4"),
            ("FUND", "To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.", 2, "#45B7D1"),
            ("COLLECT", "To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.", 3, "#96CEB4"),
            ("PROCESS", "To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.", 4, "#FECA57"),
            ("ANALYSE", "To derive insights, knowledge, and understanding from processed data.", 5, "#FF9FF3"),
            ("STORE", "To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.", 6, "#54A0FF"),
            ("PUBLISH", "To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.", 7, "#5F27CD"),
            ("PRESERVE", "To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.", 8, "#00D2D3"),
            ("SHARE", "To make data available and accessible to humans and/or machines.", 9, "#FF9F43"),
            ("ACCESS", "To control and manage data access by designated users and reusers.", 10, "#10AC84"),
            ("TRANSFORM", "To create new data from the original, for example by migration into a different format or by creating a subset.", 11, "#EE5A24")
        ]
        
        # Create stage records
        stage_objects = {}
        for name, desc, pos, color in stages_data:
            stage = MaldrethStage(name=name, description=desc, position=pos, color=color)
            db.session.add(stage)
            stage_objects[name] = stage
        
        db.session.flush()  # Ensure stages have IDs before creating relationships
        
        # Create tool categories and exemplar tools from MaLDReTH 1.0 outputs
        tools_catalog = {
            "CONCEPTUALISE": [
                ("Mind mapping, concept mapping and knowledge modelling", "Tools that define the entities of research and their relationships", ["Miro", "Meister Labs (MindMeister + MeisterTask)", "XMind"]),
                ("Diagramming and flowchart", "Tools that detail the research workflow", ["Lucidchart", "Draw.io (now Diagrams.net)", "Creately"]),
                ("Wireframing and prototyping", "Tools that visualise and demonstrate the research workflow", ["Balsamiq", "Figma"])
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
        
        # Create categories and tools
        for stage_name, categories in tools_catalog.items():
            stage_obj = stage_objects[stage_name]
            for cat_name, cat_desc, tools in categories:
                category_obj = ToolCategory(name=cat_name, description=cat_desc, stage_id=stage_obj.id)
                db.session.add(category_obj)
                db.session.flush()  # Get category ID
                
                for tool_name in tools:
                    tool_obj = ExemplarTool(
                        name=tool_name,
                        stage_id=stage_obj.id,
                        category_id=category_obj.id,
                        is_active=True
                    )
                    db.session.add(tool_obj)
        
        # Create basic stage connections for lifecycle flow
        connections_data = [
            ("CONCEPTUALISE", "PLAN", "solid"),
            ("PLAN", "FUND", "solid"),
            ("FUND", "COLLECT", "solid"),
            ("COLLECT", "PROCESS", "solid"),
            ("PROCESS", "ANALYSE", "solid"),
            ("ANALYSE", "STORE", "dashed"),
            ("STORE", "PUBLISH", "solid"),
            ("PUBLISH", "PRESERVE", "solid"),
            ("PRESERVE", "SHARE", "solid"),
            ("SHARE", "ACCESS", "solid"),
            ("ACCESS", "TRANSFORM", "dashed"),
            ("TRANSFORM", "PROCESS", "dashed")  # Transformation can loop back to processing
        ]
        
        for from_name, to_name, conn_type in connections_data:
            connection = Connection(
                from_stage_id=stage_objects[from_name].id,
                to_stage_id=stage_objects[to_name].id,
                connection_type=conn_type
            )
            db.session.add(connection)
        
        db.session.commit()
        logger.info("Database initialized with comprehensive MaLDReTH 1.0 data")
        
    except Exception as e:
        logger.error(f"Error populating MaLDReTH data: {e}")
        db.session.rollback()
        raise


# Application instance creation and CLI handling
# For LLM/Copilot: This section handles different execution contexts

if __name__ == '__main__':
    # Handle CLI commands for database management
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        # Database initialization command
        logger.info("Starting database initialization...")
        app = create_app()
        try:
            init_database_with_maldreth_data(app)
            logger.info("Database initialization completed successfully")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            sys.exit(1)
    else:
        # Development server execution
        logger.info("Starting development server...")
        app = create_app()
        
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        
        # Run development server with debug based on configuration
        debug_mode = app.config.get('DEBUG', False)
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
else:
    # Production deployment (gunicorn/uwsgi import)
    logger.info("Creating application instance for production deployment")
    app = create_app()


# Export the create_app function and app instance for external use
# For LLM/Copilot: These are the primary interfaces for the application
__all__ = ['create_app', 'app', 'init_database_with_maldreth_data']