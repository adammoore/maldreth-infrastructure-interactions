"""
routes.py
Flask routes and view functions for the MaLDReTH application.

This module contains all the routes and view functions for the web interface,
including form handling, data display, and API endpoints.
"""

import logging
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, jsonify, session, send_from_directory
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, func

# Import from extensions module to avoid circular imports
from extensions import db
from models import (
    Stage, ToolCategory, Tool, Connection, SiteInteraction, UserInteraction
)
from database import (
    get_all_stages, get_stage_by_name, get_tools_by_stage,
    get_all_connections, get_tool_categories_by_stage
)

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """
    Render the home page with lifecycle visualization.
    
    Returns:
        str: Rendered HTML template
    """
    try:
        stages = get_all_stages()
        connections = get_all_connections()
        return render_template(
            'index.html',
            stages=stages,
            connections=connections
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return render_template(
            'index.html',
            stages=[],
            connections=[],
            error="Error loading data"
        )


@main.route('/stage/<stage_name>')
def stage_detail(stage_name):
    """
    Display detailed information about a specific stage.
    
    Args:
        stage_name (str): Name of the stage to display
        
    Returns:
        str: Rendered HTML template
    """
    try:
        stage = get_stage_by_name(stage_name)
        if not stage:
            flash(f"Stage '{stage_name}' not found", 'error')
            return redirect(url_for('main.index'))
        
        tool_categories = get_tool_categories_by_stage(stage.id)
        tools = get_tools_by_stage(stage.id)
        
        return render_template(
            'stage_detail.html',
            stage=stage,
            tool_categories=tool_categories,
            tools=tools
        )
    except Exception as e:
        logger.error(f"Error displaying stage detail: {e}")
        flash("Error loading stage information", 'error')
        return redirect(url_for('main.index'))


@main.route('/submit-interaction', methods=['POST'])
def submit_interaction():
    """
    Handle form submission for user interactions.
    
    Returns:
        Response: JSON response or redirect
    """
    try:
        # Get form data
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
            return redirect(url_for('main.index'))
        
        # Create user interaction record
        interaction = UserInteraction(
            name=name,
            email=email,
            organization=organization,
            role=role,
            feedback=feedback,
            submitted_at=datetime.utcnow()
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        logger.info(f"User interaction recorded: {email}")
        
        if request.is_json:
            return jsonify({'message': 'Thank you for your feedback!'}), 200
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('main.index'))
        
    except SQLAlchemyError as e:
        logger.error(f"Database error submitting interaction: {e}")
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Database error'}), 500
        flash('Error submitting feedback. Please try again.', 'error')
        return redirect(url_for('main.index'))
    except Exception as e:
        logger.error(f"Error submitting interaction: {e}")
        if request.is_json:
            return jsonify({'error': 'Internal error'}), 500
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('main.index'))


@main.route('/view-all')
def view_all():
    """
    Display all user interactions (admin view).
    
    Returns:
        str: Rendered HTML template
    """
    try:
        # Get all interactions ordered by submission date
        interactions = UserInteraction.query.order_by(
            desc(UserInteraction.submitted_at)
        ).all()
        
        # Get summary statistics
        total_interactions = len(interactions)
        unique_emails = db.session.query(
            func.count(func.distinct(UserInteraction.email))
        ).scalar()
        
        return render_template(
            'view_all.html',
            interactions=interactions,
            total_interactions=total_interactions,
            unique_emails=unique_emails
        )
    except Exception as e:
        logger.error(f"Error viewing interactions: {e}")
        return render_template(
            'view_all.html',
            interactions=[],
            total_interactions=0,
            unique_emails=0,
            error="Error loading interactions"
        )


@main.route('/api/stages')
def api_stages():
    """
    API endpoint to get all stages.
    
    Returns:
        Response: JSON response with stages data
    """
    try:
        stages = get_all_stages()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'position': s.position
        } for s in stages])
    except Exception as e:
        logger.error(f"API error getting stages: {e}")
        return jsonify({'error': 'Error retrieving stages'}), 500


@main.route('/api/tools/<stage_name>')
def api_tools(stage_name):
    """
    API endpoint to get tools for a specific stage.
    
    Args:
        stage_name (str): Name of the stage
        
    Returns:
        Response: JSON response with tools data
    """
    try:
        stage = get_stage_by_name(stage_name)
        if not stage:
            return jsonify({'error': 'Stage not found'}), 404
        
        tools = get_tools_by_stage(stage.id)
        return jsonify([{
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'url': t.url,
            'category': t.category.name if t.category else None
        } for t in tools])
    except Exception as e:
        logger.error(f"API error getting tools: {e}")
        return jsonify({'error': 'Error retrieving tools'}), 500


@main.route('/api/docs')
def api_docs():
    """
    Display API documentation.
    
    Returns:
        str: Rendered HTML template
    """
    return render_template('api_docs.html')


@main.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    logger.warning(f"404 error: {e}")
    return render_template('error.html', error="Page not found"), 404


@main.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    logger.error(f"500 error: {e}")
    return render_template('error.html', error="Internal server error"), 500
