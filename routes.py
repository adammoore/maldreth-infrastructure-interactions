"""
Routes module for MaLDReTH Infrastructure Interactions application.

This module defines all the web routes and API endpoints for the Flask application.
It uses Flask blueprints for better organization and includes comprehensive error handling.
"""

import os
import csv
import io
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import (
    Blueprint, render_template, request, redirect, url_for, 
    flash, jsonify, make_response, current_app
)
from flask_cors import CORS

# Import db from app module to avoid circular import
from app import db
from models import Interaction
from forms import InteractionForm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
main = Blueprint('main', __name__)

# Enable CORS for API endpoints
CORS(main, resources={r"/api/*": {"origins": "*"}})


@main.route('/')
def index():
    """
    Render the home page with recent interactions and statistics.
    
    Returns:
        Rendered HTML template with interaction statistics and recent entries.
    """
    try:
        # Get interaction statistics
        total_interactions = Interaction.query.count()
        interaction_types = db.session.query(
            Interaction.interaction_type,
            db.func.count(Interaction.id)
        ).group_by(Interaction.interaction_type).all()
        
        lifecycle_stages = db.session.query(
            Interaction.lifecycle_stage,
            db.func.count(Interaction.id)
        ).group_by(Interaction.lifecycle_stage).all()
        
        # Get recent interactions (last 5)
        recent_interactions = Interaction.query.order_by(
            Interaction.created_at.desc()
        ).limit(5).all()
        
        return render_template(
            'index.html',
            total_interactions=total_interactions,
            interaction_types=interaction_types,
            lifecycle_stages=lifecycle_stages,
            recent_interactions=recent_interactions
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        flash('An error occurred while loading the page.', 'error')
        return render_template(
            'index.html',
            total_interactions=0,
            interaction_types=[],
            lifecycle_stages=[],
            recent_interactions=[]
        )


@main.route('/add', methods=['GET', 'POST'])
def add_interaction():
    """
    Handle adding new infrastructure interactions.
    
    Returns:
        GET: Rendered form template
        POST: Redirect to success page or form with errors
    """
    form = InteractionForm()
    
    if form.validate_on_submit():
        try:
            interaction = Interaction(
                interaction_type=form.interaction_type.data,
                source_infrastructure=form.source_infrastructure.data,
                target_infrastructure=form.target_infrastructure.data,
                lifecycle_stage=form.lifecycle_stage.data,
                description=form.description.data,
                technical_details=form.technical_details.data,
                standards_protocols=form.standards_protocols.data,
                benefits=form.benefits.data,
                challenges=form.challenges.data,
                examples=form.examples.data,
                contact_person=form.contact_person.data,
                organization=form.organization.data,
                email=form.email.data,
                priority=form.priority.data,
                complexity=form.complexity.data,
                status=form.status.data,
                notes=form.notes.data
            )
            
            db.session.add(interaction)
            db.session.commit()
            
            logger.info(f"New interaction added: {interaction.id}")
            flash('Interaction added successfully!', 'success')
            return redirect(url_for('main.view_interaction', id=interaction.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding interaction: {str(e)}")
            flash('An error occurred while saving the interaction.', 'error')
    
    return render_template('add_interaction.html', form=form)


@main.route('/view-all')
def view_all():
    """
    Display all interactions with filtering and pagination.
    
    Returns:
        Rendered template with paginated interactions.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
        
        # Get filter parameters
        interaction_type_filter = request.args.get('interaction_type')
        lifecycle_stage_filter = request.args.get('lifecycle_stage')
        search = request.args.get('search')
        
        # Build query
        query = Interaction.query
        
        if interaction_type_filter:
            query = query.filter(Interaction.interaction_type == interaction_type_filter)
        
        if lifecycle_stage_filter:
            query = query.filter(Interaction.lifecycle_stage == lifecycle_stage_filter)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Interaction.source_infrastructure.ilike(search_term),
                    Interaction.target_infrastructure.ilike(search_term),
                    Interaction.description.ilike(search_term),
                    Interaction.organization.ilike(search_term)
                )
            )
        
        # Paginate results
        interactions = query.order_by(Interaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get filter options
        interaction_types = db.session.query(Interaction.interaction_type).distinct().all()
        lifecycle_stages = db.session.query(Interaction.lifecycle_stage).distinct().all()
        
        return render_template(
            'view_all.html',
            interactions=interactions,
            interaction_types=[t[0] for t in interaction_types if t[0]],
            lifecycle_stages=[s[0] for s in lifecycle_stages if s[0]],
            current_filters={
                'interaction_type': interaction_type_filter,
                'lifecycle_stage': lifecycle_stage_filter,
                'search': search
            }
        )
        
    except Exception as e:
        logger.error(f"Error viewing interactions: {str(e)}")
        flash('An error occurred while loading interactions.', 'error')
        return render_template('error.html', 
                             error_code=500, 
                             error_message="view_all.html")


@main.route('/view/<int:id>')
def view_interaction(id: int):
    """
    Display detailed view of a specific interaction.
    
    Args:
        id: Interaction ID
        
    Returns:
        Rendered interaction detail template.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        return render_template('view_interaction.html', interaction=interaction)
    except Exception as e:
        logger.error(f"Error viewing interaction {id}: {str(e)}")
        flash('Interaction not found.', 'error')
        return redirect(url_for('main.view_all'))


    """
    Handle editing of existing interactions.
    
    Args:
        id: Interaction ID
        
    Returns:
        GET: Rendered edit form
        POST: Redirect to interaction view or form with errors
    """
    interaction = Interaction.query.get_or_404(id)
    form = InteractionForm(obj=interaction)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(interaction)
            interaction.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Interaction updated: {interaction.id}")
            flash('Interaction updated successfully!', 'success')
            return redirect(url_for('main.view_interaction', id=interaction.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating interaction {id}: {str(e)}")
            flash('An error occurred while updating the interaction.', 'error')
    
    return render_template('edit_interaction.html', form=form, interaction=interaction)


@main.route('/delete/<int:id>', methods=['POST'])
def delete_interaction(id: int):
    """
    Handle deletion of interactions.
    
    Args:
        id: Interaction ID
        
    Returns:
        Redirect to view all page with status message.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        db.session.delete(interaction)
        db.session.commit()
        
        logger.info(f"Interaction deleted: {id}")
        flash('Interaction deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting interaction {id}: {str(e)}")
        flash('An error occurred while deleting the interaction.', 'error')
    
    return redirect(url_for('main.view_all'))


@main.route('/export/csv')
def export_csv():
    """
    Export all interactions to CSV format.
    
    Returns:
        CSV file download response.
    """
    try:
        interactions = Interaction.query.order_by(Interaction.created_at.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = [
            'ID', 'Interaction Type', 'Source Infrastructure', 'Target Infrastructure',
            'Lifecycle Stage', 'Description', 'Technical Details', 'Standards/Protocols',
            'Benefits', 'Challenges', 'Examples', 'Contact Person', 'Organization',
            'Email', 'Priority', 'Complexity', 'Status', 'Notes', 'Created At', 'Updated At'
        ]
        writer.writerow(header)
        
        # Write data
        for interaction in interactions:
            row = [
                interaction.id,
                interaction.interaction_type,
                interaction.source_infrastructure,
                interaction.target_infrastructure,
                interaction.lifecycle_stage,
                interaction.description,
                interaction.technical_details,
                interaction.standards_protocols,
                interaction.benefits,
                interaction.challenges,
                interaction.examples,
                interaction.contact_person,
                interaction.organization,
                interaction.email,
                interaction.priority,
                interaction.complexity,
                interaction.status,
                interaction.notes,
                interaction.created_at.isoformat() if interaction.created_at else '',
                interaction.updated_at.isoformat() if interaction.updated_at else ''
            ]
            writer.writerow(row)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=maldreth_interactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        logger.info("CSV export completed")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        flash('An error occurred while exporting data.', 'error')
        return redirect(url_for('main.view_all'))


@main.route('/api/docs')
def api_docs():
    """
    Render API documentation page.
    
    Returns:
        Rendered API documentation template.
    """
    return render_template('api_docs.html')


# API Routes
@main.route('/api/interactions', methods=['GET'])
def api_get_interactions():
    """
    API endpoint to retrieve all interactions.
    
    Returns:
        JSON response with interactions data.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 100, type=int), 100)
        
        interactions = Interaction.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'interactions': [interaction.to_dict() for interaction in interactions.items],
            'pagination': {
                'page': interactions.page,
                'pages': interactions.pages,
                'per_page': interactions.per_page,
                'total': interactions.total,
                'has_next': interactions.has_next,
                'has_prev': interactions.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"API error getting interactions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@main.route('/api/interactions', methods=['POST'])
def api_create_interaction():
    """
    API endpoint to create new interaction.
    
    Returns:
        JSON response with created interaction data.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = [
            'interaction_type', 'source_infrastructure', 
            'target_infrastructure', 'lifecycle_stage', 'description'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        interaction = Interaction(**data)
        db.session.add(interaction)
        db.session.commit()
        
        logger.info(f"API: New interaction created: {interaction.id}")
        return jsonify(interaction.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"API error creating interaction: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@main.route('/api/interactions/<int:id>', methods=['GET'])
def api_get_interaction(id: int):
    """
    API endpoint to retrieve specific interaction.
    
    Args:
        id: Interaction ID
        
    Returns:
        JSON response with interaction data.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        return jsonify(interaction.to_dict())
        
    except Exception as e:
        logger.error(f"API error getting interaction {id}: {str(e)}")
        return jsonify({'error': 'Interaction not found'}), 404


@main.route('/api/interactions/<int:id>', methods=['PUT'])
def api_update_interaction(id: int):
    """
    API endpoint to update specific interaction.
    
    Args:
        id: Interaction ID
        
    Returns:
        JSON response with updated interaction data.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        for field, value in data.items():
            if hasattr(interaction, field):
                setattr(interaction, field, value)
        
        interaction.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"API: Interaction updated: {interaction.id}")
        return jsonify(interaction.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"API error updating interaction {id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@main.route('/api/interactions/<int:id>', methods=['DELETE'])
def api_delete_interaction(id: int):
    """
    API endpoint to delete specific interaction.
    
    Args:
        id: Interaction ID
        
    Returns:
        JSON response confirming deletion.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        db.session.delete(interaction)
        db.session.commit()
        
        logger.info(f"API: Interaction deleted: {id}")
        return jsonify({'message': 'Interaction deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"API error deleting interaction {id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@main.route('/api/stats')
def api_get_stats():
    """
    API endpoint to retrieve interaction statistics.
    
    Returns:
        JSON response with statistics data.
    """
    try:
        total_interactions = Interaction.query.count()
        
        interaction_types = db.session.query(
            Interaction.interaction_type,
            db.func.count(Interaction.id)
        ).group_by(Interaction.interaction_type).all()
        
        lifecycle_stages = db.session.query(
            Interaction.lifecycle_stage,
            db.func.count(Interaction.id)
        ).group_by(Interaction.lifecycle_stage).all()
        
        return jsonify({
            'total_interactions': total_interactions,
            'interaction_types': {t[0]: t[1] for t in interaction_types},
            'lifecycle_stages': {s[0]: s[1] for s in lifecycle_stages}
        })
        
    except Exception as e:
        logger.error(f"API error getting stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Error Handlers
@main.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404


@main.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return render_template('error.html',
                         error_code=500,
                         error_message="Internal server error"), 500


@main.errorhandler(Exception)
def handle_exception(error):
    """Handle all other exceptions."""
    db.session.rollback()
    logger.error(f"Unhandled exception: {str(error)}")
    return render_template('error.html',
                         error_code=500,
                         error_message="An unexpected error occurred"), 500


# Template context processor
@main.context_processor
def inject_template_vars():
    """Inject variables into all templates."""
    return {
        'current_year': datetime.now().year,
        'app_version': current_app.config.get('VERSION', '1.0.0')
    }


def help():
    """
    Display help information for the routes module.
    
    This function provides comprehensive information about all available routes,
    their purposes, and usage examples.
    """
    print("""
    MaLDReTH Infrastructure Interactions - Routes Module
    ==================================================
    
    This module defines all web routes and API endpoints for the Flask application.
    
    Web Routes:
    -----------
    /                   - Home page with statistics and recent interactions
    /add               - Form to add new interaction
    /view-all          - List all interactions with filtering
    /view/<id>         - View specific interaction details
    /edit/<id>         - Edit existing interaction
    /delete/<id>       - Delete interaction (POST only)
    /export/csv        - Export all interactions to CSV
    /api/docs          - API documentation
    
    API Endpoints:
    --------------
    GET    /api/interactions       - List all interactions (paginated)
    POST   /api/interactions       - Create new interaction
    GET    /api/interactions/<id>  - Get specific interaction
    PUT    /api/interactions/<id>  - Update specific interaction
    DELETE /api/interactions/<id>  - Delete specific interaction
    GET    /api/stats              - Get interaction statistics
    
    Error Handling:
    ---------------
    The module includes comprehensive error handling for:
    - 404 Not Found errors
    - 500 Internal Server errors
    - General exceptions with logging
    
    Usage Example:
    --------------
    from routes import main
    app.register_blueprint(main)
    
    For more information, see the API documentation at /api/docs
    """)


if __name__ == '__main__':
    help()
    """
Routes module for MaLDReTH Infrastructure Interactions application.

This module defines all the web routes and API endpoints for the Flask application.
It uses Flask blueprints for better organization and includes comprehensive error handling.
"""

import os
import csv
import io
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import (
    Blueprint, render_template, request, redirect, url_for, 
    flash, jsonify, make_response, current_app
)
from flask_cors import CORS

from models import Interaction, db
from forms import InteractionForm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
main = Blueprint('main', __name__)

# Enable CORS for API endpoints
CORS(main, resources={r"/api/*": {"origins": "*"}})


@main.route('/')
def index():
    """
    Render the home page with recent interactions and statistics.
    
    Returns:
        Rendered HTML template with interaction statistics and recent entries.
    """
    try:
        # Get interaction statistics
        total_interactions = Interaction.query.count()
        interaction_types = db.session.query(
            Interaction.interaction_type,
            db.func.count(Interaction.id)
        ).group_by(Interaction.interaction_type).all()
        
        lifecycle_stages = db.session.query(
            Interaction.lifecycle_stage,
            db.func.count(Interaction.id)
        ).group_by(Interaction.lifecycle_stage).all()
        
        # Get recent interactions (last 5)
        recent_interactions = Interaction.query.order_by(
            Interaction.created_at.desc()
        ).limit(5).all()
        
        return render_template(
            'index.html',
            total_interactions=total_interactions,
            interaction_types=interaction_types,
            lifecycle_stages=lifecycle_stages,
            recent_interactions=recent_interactions
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        flash('An error occurred while loading the page.', 'error')
        return render_template(
            'index.html',
            total_interactions=0,
            interaction_types=[],
            lifecycle_stages=[],
            recent_interactions=[]
        )


@main.route('/add', methods=['GET', 'POST'])
def add_interaction():
    """
    Handle adding new infrastructure interactions.
    
    Returns:
        GET: Rendered form template
        POST: Redirect to success page or form with errors
    """
    form = InteractionForm()
    
    if form.validate_on_submit():
        try:
            interaction = Interaction(
                interaction_type=form.interaction_type.data,
                source_infrastructure=form.source_infrastructure.data,
                target_infrastructure=form.target_infrastructure.data,
                lifecycle_stage=form.lifecycle_stage.data,
                description=form.description.data,
                technical_details=form.technical_details.data,
                standards_protocols=form.standards_protocols.data,
                benefits=form.benefits.data,
                challenges=form.challenges.data,
                examples=form.examples.data,
                contact_person=form.contact_person.data,
                organization=form.organization.data,
                email=form.email.data,
                priority=form.priority.data,
                complexity=form.complexity.data,
                status=form.status.data,
                notes=form.notes.data
            )
            
            db.session.add(interaction)
            db.session.commit()
            
            logger.info(f"New interaction added: {interaction.id}")
            flash('Interaction added successfully!', 'success')
            return redirect(url_for('main.view_interaction', id=interaction.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding interaction: {str(e)}")
            flash('An error occurred while saving the interaction.', 'error')
    
    return render_template('add_interaction.html', form=form)


@main.route('/view-all')
def view_all():
    """
    Display all interactions with filtering and pagination.
    
    Returns:
        Rendered template with paginated interactions.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
        
        # Get filter parameters
        interaction_type_filter = request.args.get('interaction_type')
        lifecycle_stage_filter = request.args.get('lifecycle_stage')
        search = request.args.get('search')
        
        # Build query
        query = Interaction.query
        
        if interaction_type_filter:
            query = query.filter(Interaction.interaction_type == interaction_type_filter)
        
        if lifecycle_stage_filter:
            query = query.filter(Interaction.lifecycle_stage == lifecycle_stage_filter)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Interaction.source_infrastructure.ilike(search_term),
                    Interaction.target_infrastructure.ilike(search_term),
                    Interaction.description.ilike(search_term),
                    Interaction.organization.ilike(search_term)
                )
            )
        
        # Paginate results
        interactions = query.order_by(Interaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get filter options
        interaction_types = db.session.query(Interaction.interaction_type).distinct().all()
        lifecycle_stages = db.session.query(Interaction.lifecycle_stage).distinct().all()
        
        return render_template(
            'view_all.html',
            interactions=interactions,
            interaction_types=[t[0] for t in interaction_types if t[0]],
            lifecycle_stages=[s[0] for s in lifecycle_stages if s[0]],
            current_filters={
                'interaction_type': interaction_type_filter,
                'lifecycle_stage': lifecycle_stage_filter,
                'search': search
            }
        )
        
    except Exception as e:
        logger.error(f"Error viewing interactions: {str(e)}")
        flash('An error occurred while loading interactions.', 'error')
        return render_template('view_all.html', interactions=None)


@main.route('/view/<int:id>')
def view_interaction(id: int):
    """
    Display detailed view of a specific interaction.
    
    Args:
        id: Interaction ID
        
    Returns:
        Rendered interaction detail template.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        return render_template('view_interaction.html', interaction=interaction)
    except Exception as e:
        logger.error(f"Error viewing interaction {id}: {str(e)}")
        flash('Interaction not found.', 'error')
        return redirect(url_for('main.view_all'))


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_interaction(id: int):
    """
    Handle editing of existing interactions.
    
    Args:
        id: Interaction ID
        
    Returns:
        GET: Rendered edit form
        POST: Redirect to interaction view or form with errors
    """
    interaction = Interaction.query.get_or_404(id)
    form = InteractionForm(obj=interaction)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(interaction)
            interaction.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Interaction updated: {interaction.id}")
            flash('Interaction updated successfully!', 'success')
            return redirect(url_for('main.view_interaction', id=interaction.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating interaction {id}: {str(e)}")
            flash('An error occurred while updating the interaction.', 'error')
    
    return render_template('edit_interaction.html', form=form, interaction=interaction)


@main.route('/delete/<int:id>', methods=['POST'])
def delete_interaction(id: int):
    """
    Handle deletion of interactions.
    
    Args:
        id: Interaction ID
        
    Returns:
        Redirect to view all page with status message.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        db.session.delete(interaction)
        db.session.commit()
        
        logger.info(f"Interaction deleted: {id}")
        flash('Interaction deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting interaction {id}: {str(e)}")
        flash('An error occurred while deleting the interaction.', 'error')
    
    return redirect(url_for('main.view_all'))


@main.route('/export/csv')
def export_csv():
    """
    Export all interactions to CSV format.
    
    Returns:
        CSV file download response.
    """
    try:
        interactions = Interaction.query.order_by(Interaction.created_at.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = [
            'ID', 'Interaction Type', 'Source Infrastructure', 'Target Infrastructure',
            'Lifecycle Stage', 'Description', 'Technical Details', 'Standards/Protocols',
            'Benefits', 'Challenges', 'Examples', 'Contact Person', 'Organization',
            'Email', 'Priority', 'Complexity', 'Status', 'Notes', 'Created At', 'Updated At'
        ]
        writer.writerow(header)
        
        # Write data
        for interaction in interactions:
            row = [
                interaction.id,
                interaction.interaction_type,
                interaction.source_infrastructure,
                interaction.target_infrastructure,
                interaction.lifecycle_stage,
                interaction.description,
                interaction.technical_details,
                interaction.standards_protocols,
                interaction.benefits,
                interaction.challenges,
                interaction.examples,
                interaction.contact_person,
                interaction.organization,
                interaction.email,
                interaction.priority,
                interaction.complexity,
                interaction.status,
                interaction.notes,
                interaction.created_at.isoformat() if interaction.created_at else '',
                interaction.updated_at.isoformat() if interaction.updated_at else ''
            ]
            writer.writerow(row)
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=maldreth_interactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        logger.info("CSV export completed")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        flash('An error occurred while exporting data.', 'error')
        return redirect(url_for('main.view_all'))


@main.route('/api/docs')
def api_docs():
    """
    Render API documentation page.
    
    Returns:
        Rendered API documentation template.
    """
    return render_template('api_docs.html')


# API Routes
@main.route('/api/interactions', methods=['GET'])
def api_get_interactions():
    """
    API endpoint to retrieve all interactions.
    
    Returns:
        JSON response with interactions data.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 100, type=int), 100)
        
        interactions = Interaction.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'interactions': [interaction.to_dict() for interaction in interactions.items],
            'pagination': {
                'page': interactions.page,
                'pages': interactions.pages,
                'per_page': interactions.per_page,
                'total': interactions.total,
                'has_next': interactions.has_next,
                'has_prev': interactions.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"API error getting interactions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@main.route('/api/interactions', methods=['POST'])
def api_create_interaction():
    """
    API endpoint to create new interaction.
    
    Returns:
        JSON response with created interaction data.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = [
            'interaction_type', 'source_infrastructure', 
            'target_infrastructure', 'lifecycle_stage', 'description'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        interaction = Interaction(**data)
        db.session.add(interaction)
        db.session.commit()
        
        logger.info(f"API: New interaction created: {interaction.id}")
        return jsonify(interaction.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"API error creating interaction: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@main.route('/api/interactions/<int:id>', methods=['GET'])
def api_get_interaction(id: int):
    """
    API endpoint to retrieve specific interaction.
    
    Args:
        id: Interaction ID
        
    Returns:
        JSON response with interaction data.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        return jsonify(interaction.to_dict())
        
    except Exception as e:
        logger.error(f"API error getting interaction {id}: {str(e)}")
        return jsonify({'error': 'Interaction not found'}), 404


@main.route('/api/interactions/<int:id>', methods=['PUT'])
def api_update_interaction(id: int):
    """
    API endpoint to update specific interaction.
    
    Args:
        id: Interaction ID
        
    Returns:
        JSON response with updated interaction data.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        for field, value in data.items():
            if hasattr(interaction, field):
                setattr(interaction, field, value)
        
        interaction.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"API: Interaction updated: {interaction.id}")
        return jsonify(interaction.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"API error updating interaction {id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@main.route('/api/interactions/<int:id>', methods=['DELETE'])
def api_delete_interaction(id: int):
    """
    API endpoint to delete specific interaction.
    
    Args:
        id: Interaction ID
        
    Returns:
        JSON response confirming deletion.
    """
    try:
        interaction = Interaction.query.get_or_404(id)
        db.session.delete(interaction)
        db.session.commit()
        
        logger.info(f"API: Interaction deleted: {id}")
        return jsonify({'message': 'Interaction deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"API error deleting interaction {id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@main.route('/api/stats')
def api_get_stats():
    """
    API endpoint to retrieve interaction statistics.
    
    Returns:
        JSON response with statistics data.
    """
    try:
        total_interactions = Interaction.query.count()
        
        interaction_types = db.session.query(
            Interaction.interaction_type,
            db.func.count(Interaction.id)
        ).group_by(Interaction.interaction_type).all()
        
        lifecycle_stages = db.session.query(
            Interaction.lifecycle_stage,
            db.func.count(Interaction.id)
        ).group_by(Interaction.lifecycle_stage).all()
        
        return jsonify({
            'total_interactions': total_interactions,
            'interaction_types': {t[0]: t[1] for t in interaction_types},
            'lifecycle_stages': {s[0]: s[1] for s in lifecycle_stages}
        })
        
    except Exception as e:
        logger.error(f"API error getting stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Error Handlers
@main.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404


@main.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return render_template('error.html',
                         error_code=500,
                         error_message="Internal server error"), 500


@main.errorhandler(Exception)
def handle_exception(error):
    """Handle all other exceptions."""
    db.session.rollback()
    logger.error(f"Unhandled exception: {str(error)}")
    return render_template('error.html',
                         error_code=500,
                         error_message="An unexpected error occurred"), 500


# Template context processor
@main.context_processor
def inject_template_vars():
    """Inject variables into all templates."""
    return {
        'current_year': datetime.now().year,
        'app_version': current_app.config.get('VERSION', '1.0.0')
    }


def help():
    """
    Display help information for the routes module.
    
    This function provides comprehensive information about all available routes,
    their purposes, and usage examples.
    """
    print("""
    MaLDReTH Infrastructure Interactions - Routes Module
    ==================================================
    
    This module defines all web routes and API endpoints for the Flask application.
    
    Web Routes:
    -----------
    /                   - Home page with statistics and recent interactions
    /add               - Form to add new interaction
    /view-all          - List all interactions with filtering
    /view/<id>         - View specific interaction details
    /edit/<id>         - Edit existing interaction
    /delete/<id>       - Delete interaction (POST only)
    /export/csv        - Export all interactions to CSV
    /api/docs          - API documentation
    
    API Endpoints:
    --------------
    GET    /api/interactions       - List all interactions (paginated)
    POST   /api/interactions       - Create new interaction
    GET    /api/interactions/<id>  - Get specific interaction
    PUT    /api/interactions/<id>  - Update specific interaction
    DELETE /api/interactions/<id>  - Delete specific interaction
    GET    /api/stats              - Get interaction statistics
    
    Error Handling:
    ---------------
    The module includes comprehensive error handling for:
    - 404 Not Found errors
    - 500 Internal Server errors
    - General exceptions with logging
    
    Usage Example:
    --------------
    from routes import main
    app.register_blueprint(main)
    
    For more information, see the API documentation at /api/docs
    """)


if __name__ == '__main__':
    help()
