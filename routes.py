"""
routes.py

Main routes for the MaLDReTH Infrastructure Interactions application.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from models import db, Interaction

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Main page with overview and navigation."""
    try:
        interaction_count = Interaction.query.count()
        recent_interactions = (
            Interaction.query.order_by(Interaction.created_at.desc()).limit(5).all()
        )

        return render_template(
            'index.html',
            interaction_count=interaction_count,
            recent_interactions=recent_interactions,
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        flash("Error loading dashboard data", "error")
        return render_template(
            'index.html', interaction_count=0, recent_interactions=[]
        )


@main_bp.route('/add')
def add_interaction():
    """Form for adding new interactions."""
    return render_template('add_interaction.html')


@main_bp.route('/interactions')
def view_interactions():
    """View all interactions."""
    try:
        page = request.args.get('page', 1, type=int)
        interactions = Interaction.query.order_by(
            Interaction.created_at.desc()
        ).paginate(
            page=page, 
            per_page=20, 
            error_out=False
        )
        return render_template('interactions.html', interactions=interactions)
    except Exception as e:
        logger.error(f"Error viewing interactions: {e}")
        flash("Error loading interactions", "error")
        return render_template('interactions.html', interactions=None)


@main_bp.route('/tools/explorer')
def tools_explorer():
    """Tool explorer page."""
    return render_template('tools/explorer.html')


@main_bp.route('/dashboard/visualization')
def visualization_dashboard():
    """Visualization dashboard page."""
    return render_template('dashboard/visualization.html')


@main_bp.route('/interactions/builder')
def interaction_builder():
    """Interaction builder page."""
    return render_template('interactions/builder.html')


@main_bp.route('/submit', methods=['POST'])
def submit_interaction():
    """Handle form submission for new interactions."""
    try:
        # Validate required fields
        required_fields = [
            'interaction_type',
            'source_infrastructure',
            'target_infrastructure',
            'lifecycle_stage',
            'description',
        ]

        for field in required_fields:
            if not request.form.get(field):
                flash(f"Missing required field: {field}", "error")
                return render_template(
                    'add_interaction.html',
                    form_data=request.form,
                )

        # Create new interaction
        interaction = Interaction(
            interaction_type=request.form['interaction_type'],
            source_infrastructure=request.form['source_infrastructure'],
            target_infrastructure=request.form['target_infrastructure'],
            lifecycle_stage=request.form['lifecycle_stage'],
            description=request.form['description'],
            technical_details=request.form.get('technical_details'),
            benefits=request.form.get('benefits'),
            challenges=request.form.get('challenges'),
            examples=request.form.get('examples'),
            contact_person=request.form.get('contact_person'),
            organization=request.form.get('organization'),
            email=request.form.get('email'),
            priority=request.form.get('priority', 'medium'),
            complexity=request.form.get('complexity', 'moderate'),
            status=request.form.get('status', 'proposed'),
        )

        # Validate the interaction
        is_valid, errors = interaction.validate()
        if not is_valid:
            for error in errors:
                flash(error, "error")
            return render_template(
                'add_interaction.html',
                form_data=request.form,
            )

        db.session.add(interaction)
        db.session.commit()

        logger.info(f"Created new interaction via form: {interaction.id}")
        flash("Interaction created successfully!", "success")
        return redirect(url_for('main.view_interactions'))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error submitting interaction: {e}")
        flash("Failed to submit interaction. Please try again.", "error")
        return render_template(
            'add_interaction.html',
            form_data=request.form,
        )


@main_bp.route('/interactions/<int:interaction_id>')
def interaction_detail(interaction_id):
    """View details for a specific interaction."""
    try:
        interaction = Interaction.query.get_or_404(interaction_id)
        return render_template('interaction_detail.html', interaction=interaction)
    except Exception as e:
        logger.error(f"Error viewing interaction {interaction_id}: {e}")
        flash("Interaction not found", "error")
        return redirect(url_for('main.view_interactions'))


@main_bp.route('/interactions/<int:interaction_id>/edit')
def edit_interaction(interaction_id):
    """Edit form for an interaction."""
    try:
        interaction = Interaction.query.get_or_404(interaction_id)
        return render_template('edit_interaction.html', interaction=interaction)
    except Exception as e:
        logger.error(f"Error loading edit form for interaction {interaction_id}: {e}")
        flash("Interaction not found", "error")
        return redirect(url_for('main.view_interactions'))


@main_bp.route('/interactions/<int:interaction_id>/update', methods=['POST'])
def update_interaction(interaction_id):
    """Update an existing interaction."""
    try:
        interaction = Interaction.query.get_or_404(interaction_id)
        
        # Update fields from form
        interaction.update_from_dict(request.form.to_dict())
        
        # Validate the updated interaction
        is_valid, errors = interaction.validate()
        if not is_valid:
            for error in errors:
                flash(error, "error")
            return render_template(
                'edit_interaction.html',
                interaction=interaction,
                form_data=request.form,
            )
        
        db.session.commit()
        
        logger.info(f"Updated interaction: {interaction.id}")
        flash("Interaction updated successfully!", "success")
        return redirect(url_for('main.interaction_detail', interaction_id=interaction.id))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating interaction {interaction_id}: {e}")
        flash("Failed to update interaction. Please try again.", "error")
        return redirect(url_for('main.edit_interaction', interaction_id=interaction_id))


@main_bp.route('/interactions/<int:interaction_id>/delete', methods=['POST'])
def delete_interaction(interaction_id):
    """Delete an interaction."""
    try:
        interaction = Interaction.query.get_or_404(interaction_id)
        db.session.delete(interaction)
        db.session.commit()
        
        logger.info(f"Deleted interaction: {interaction_id}")
        flash("Interaction deleted successfully!", "success")
        return redirect(url_for('main.view_interactions'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting interaction {interaction_id}: {e}")
        flash("Failed to delete interaction. Please try again.", "error")
        return redirect(url_for('main.view_interactions'))


@main_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500


@main_bp.errorhandler(Exception)
def handle_exception(error):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {error}")
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message="An unexpected error occurred"), 500
