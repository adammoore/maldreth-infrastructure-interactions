"""
MaLDReTH Infrastructure Interactions Collection Flask Application
=================================================================

Simplified version optimized for Heroku deployment.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional as OptionalValidator
import pandas as pd
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask application configuration
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration - Heroku provides DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Heroku provides postgres://, but SQLAlchemy needs postgresql://
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///maldreth_interactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Data Model
class InfrastructureInteraction(db.Model):
    """Model representing an infrastructure interaction."""
    __tablename__ = 'infrastructure_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    interaction_type = db.Column(db.String(100), nullable=False)
    source_infrastructure = db.Column(db.String(200), nullable=False)
    target_infrastructure = db.Column(db.String(200), nullable=False)
    lifecycle_stage = db.Column(db.String(100), nullable=False)
    interaction_description = db.Column(db.Text, nullable=False)
    technical_details = db.Column(db.Text)
    standards_protocols = db.Column(db.String(500))
    benefits = db.Column(db.Text)
    challenges = db.Column(db.Text)
    examples = db.Column(db.Text)
    contact_person = db.Column(db.String(200))
    organization = db.Column(db.String(200))
    email = db.Column(db.String(200))
    priority_level = db.Column(db.String(50))
    implementation_complexity = db.Column(db.String(50))
    current_status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'interaction_type': self.interaction_type,
            'source_infrastructure': self.source_infrastructure,
            'target_infrastructure': self.target_infrastructure,
            'lifecycle_stage': self.lifecycle_stage,
            'interaction_description': self.interaction_description,
            'technical_details': self.technical_details,
            'standards_protocols': self.standards_protocols,
            'benefits': self.benefits,
            'challenges': self.challenges,
            'examples': self.examples,
            'contact_person': self.contact_person,
            'organization': self.organization,
            'email': self.email,
            'priority_level': self.priority_level,
            'implementation_complexity': self.implementation_complexity,
            'current_status': self.current_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Forms
class InfrastructureInteractionForm(FlaskForm):
    """Form for collecting infrastructure interaction data."""
    
    interaction_type = SelectField(
        'Interaction Type',
        choices=[
            ('data_flow', 'Data Flow'),
            ('api_integration', 'API Integration'),
            ('metadata_exchange', 'Metadata Exchange'),
            ('authentication', 'Authentication/Authorization'),
            ('workflow_orchestration', 'Workflow Orchestration'),
            ('storage_federation', 'Storage Federation'),
            ('compute_federation', 'Compute Federation'),
            ('service_composition', 'Service Composition'),
            ('other', 'Other')
        ],
        validators=[DataRequired()]
    )
    
    source_infrastructure = StringField(
        'Source Infrastructure',
        validators=[DataRequired()]
    )
    
    target_infrastructure = StringField(
        'Target Infrastructure', 
        validators=[DataRequired()]
    )
    
    lifecycle_stage = SelectField(
        'Research Data Lifecycle Stage',
        choices=[
            ('conceptualise', 'Conceptualise'),
            ('plan', 'Plan'),
            ('collect', 'Collect'),
            ('process', 'Process'),
            ('analyse', 'Analyse'),
            ('store', 'Store'),
            ('publish', 'Publish'),
            ('preserve', 'Preserve'),
            ('share', 'Share'),
            ('access', 'Access'),
            ('transform', 'Transform')
        ],
        validators=[DataRequired()]
    )
    
    interaction_description = TextAreaField(
        'Interaction Description',
        validators=[DataRequired()]
    )
    
    technical_details = TextAreaField(
        'Technical Details',
        validators=[OptionalValidator()]
    )
    
    standards_protocols = StringField(
        'Standards & Protocols',
        validators=[OptionalValidator()]
    )
    
    benefits = TextAreaField(
        'Benefits',
        validators=[OptionalValidator()]
    )
    
    challenges = TextAreaField(
        'Challenges',
        validators=[OptionalValidator()]
    )
    
    examples = TextAreaField(
        'Examples',
        validators=[OptionalValidator()]
    )
    
    contact_person = StringField(
        'Contact Person',
        validators=[OptionalValidator()]
    )
    
    organization = StringField(
        'Organization',
        validators=[OptionalValidator()]
    )
    
    email = StringField(
        'Email',
        validators=[OptionalValidator()]
    )
    
    priority_level = SelectField(
        'Priority Level',
        choices=[('', 'Select Priority')] + [
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low')
        ],
        validators=[OptionalValidator()]
    )
    
    implementation_complexity = SelectField(
        'Implementation Complexity',
        choices=[('', 'Select Complexity')] + [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('very_high', 'Very High')
        ],
        validators=[OptionalValidator()]
    )
    
    current_status = SelectField(
        'Current Status',
        choices=[('', 'Select Status')] + [
            ('concept', 'Concept'),
            ('planned', 'Planned'),
            ('in_development', 'In Development'),
            ('pilot', 'Pilot'),
            ('production', 'Production'),
            ('deprecated', 'Deprecated')
        ],
        validators=[OptionalValidator()]
    )
    
    submit = SubmitField('Submit')

# Routes
@app.route('/')
def index():
    """Main landing page."""
    try:
        total_interactions = InfrastructureInteraction.query.count()
        
        stage_counts = db.session.query(
            InfrastructureInteraction.lifecycle_stage,
            db.func.count(InfrastructureInteraction.id)
        ).group_by(InfrastructureInteraction.lifecycle_stage).all()
        
        recent_interactions = InfrastructureInteraction.query.order_by(
            InfrastructureInteraction.created_at.desc()
        ).limit(5).all()
        
        return render_template('index.html',
                             total_interactions=total_interactions,
                             stage_counts=dict(stage_counts),
                             recent_interactions=recent_interactions)
    
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('index.html',
                             total_interactions=0,
                             stage_counts={},
                             recent_interactions=[])

@app.route('/add', methods=['GET', 'POST'])
def add_interaction():
    """Add a new infrastructure interaction."""
    form = InfrastructureInteractionForm()
    
    if form.validate_on_submit():
        try:
            interaction = InfrastructureInteraction(
                interaction_type=form.interaction_type.data,
                source_infrastructure=form.source_infrastructure.data,
                target_infrastructure=form.target_infrastructure.data,
                lifecycle_stage=form.lifecycle_stage.data,
                interaction_description=form.interaction_description.data,
                technical_details=form.technical_details.data,
                standards_protocols=form.standards_protocols.data,
                benefits=form.benefits.data,
                challenges=form.challenges.data,
                examples=form.examples.data,
                contact_person=form.contact_person.data,
                organization=form.organization.data,
                email=form.email.data,
                priority_level=form.priority_level.data or None,
                implementation_complexity=form.implementation_complexity.data or None,
                current_status=form.current_status.data or None
            )
            
            db.session.add(interaction)
            db.session.commit()
            
            flash('Infrastructure interaction added successfully!', 'success')
            return redirect(url_for('view_interactions'))
            
        except Exception as e:
            logger.error(f"Error adding interaction: {str(e)}")
            db.session.rollback()
            flash('An error occurred while adding the interaction.', 'error')
    
    return render_template('add_interaction.html', form=form)

@app.route('/interactions')
def view_interactions():
    """View all infrastructure interactions."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        interactions = InfrastructureInteraction.query.order_by(
            InfrastructureInteraction.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('interactions.html', interactions=interactions)
    
    except Exception as e:
        logger.error(f"Error viewing interactions: {str(e)}")
        flash('An error occurred while loading interactions.', 'error')
        return render_template('interactions.html', interactions=None)

@app.route('/api/interactions', methods=['GET'])
def api_get_interactions():
    """API endpoint to get all interactions."""
    try:
        interactions = InfrastructureInteraction.query.all()
        return jsonify({
            'success': True,
            'data': [interaction.to_dict() for interaction in interactions],
            'count': len(interactions)
        })
    except Exception as e:
        logger.error(f"Error in API get interactions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while fetching interactions'
        }), 500

@app.route('/export/csv')
def export_csv():
    """Export all interactions to CSV."""
    try:
        interactions = InfrastructureInteraction.query.all()
        data = [interaction.to_dict() for interaction in interactions]
        df = pd.DataFrame(data)
        
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'maldreth_infrastructure_interactions_{timestamp}.csv'
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")
        flash('An error occurred while exporting data.', 'error')
        return redirect(url_for('view_interactions'))

# CLI Commands
@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized successfully!")

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
