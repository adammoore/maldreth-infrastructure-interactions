"""
MaLDReTH Infrastructure Interactions Collection Flask Application
=================================================================

Simplified version that works reliably on Heroku.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
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
    
    def to_dict(self):
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
    if request.method == 'POST':
        try:
            # Get form data with validation
            required_fields = ['interaction_type', 'source_infrastructure', 
                             'target_infrastructure', 'lifecycle_stage', 
                             'interaction_description']
            
            # Check required fields
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required.', 'error')
                    return render_template('add_interaction.html')
            
            interaction = InfrastructureInteraction(
                interaction_type=request.form.get('interaction_type'),
                source_infrastructure=request.form.get('source_infrastructure'),
                target_infrastructure=request.form.get('target_infrastructure'),
                lifecycle_stage=request.form.get('lifecycle_stage'),
                interaction_description=request.form.get('interaction_description'),
                technical_details=request.form.get('technical_details'),
                standards_protocols=request.form.get('standards_protocols'),
                benefits=request.form.get('benefits'),
                challenges=request.form.get('challenges'),
                examples=request.form.get('examples'),
                contact_person=request.form.get('contact_person'),
                organization=request.form.get('organization'),
                email=request.form.get('email'),
                priority_level=request.form.get('priority_level') or None,
                implementation_complexity=request.form.get('implementation_complexity') or None,
                current_status=request.form.get('current_status') or None
            )
            
            db.session.add(interaction)
            db.session.commit()
            
            flash('Infrastructure interaction added successfully!', 'success')
            return redirect(url_for('view_interactions'))
            
        except Exception as e:
            logger.error(f"Error adding interaction: {str(e)}")
            db.session.rollback()
            flash('An error occurred while adding the interaction.', 'error')
    
    return render_template('add_interaction.html')

@app.route('/interactions')
def view_interactions():
    """View all infrastructure interactions."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        interactions = InfrastructureInteraction.query.order_by(
            InfrastructureInteraction.created_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return render_template('interactions.html', interactions=interactions)
    
    except Exception as e:
        logger.error(f"Error viewing interactions: {str(e)}")
        flash('An error occurred while loading interactions.', 'error')
        return render_template('interactions.html', interactions=None)

@app.route('/interaction/<int:id>')
def view_interaction(id):
    """View details of a specific interaction."""
    try:
        interaction = InfrastructureInteraction.query.get_or_404(id)
        return render_template('interaction_detail.html', interaction=interaction)
    except Exception as e:
        logger.error(f"Error viewing interaction {id}: {str(e)}")
        flash('An error occurred while loading the interaction.', 'error')
        return redirect(url_for('view_interactions'))

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

@app.route('/api/interactions', methods=['POST'])
def api_create_interaction():
    """API endpoint to create a new interaction."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create new interaction
        interaction = InfrastructureInteraction(
            interaction_type=data.get('interaction_type'),
            source_infrastructure=data.get('source_infrastructure'),
            target_infrastructure=data.get('target_infrastructure'),
            lifecycle_stage=data.get('lifecycle_stage'),
            interaction_description=data.get('interaction_description'),
            technical_details=data.get('technical_details'),
            standards_protocols=data.get('standards_protocols'),
            benefits=data.get('benefits'),
            challenges=data.get('challenges'),
            examples=data.get('examples'),
            contact_person=data.get('contact_person'),
            organization=data.get('organization'),
            email=data.get('email'),
            priority_level=data.get('priority_level'),
            implementation_complexity=data.get('implementation_complexity'),
            current_status=data.get('current_status')
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': interaction.to_dict(),
            'message': 'Interaction created successfully'
        }), 201
    
    except Exception as e:
        logger.error(f"Error in API create interaction: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'An error occurred while creating the interaction'
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
    with app.app_context():
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

# Database initialization for Heroku
@app.before_first_request
def create_tables():
    """Create database tables before first request."""
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 5000))
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=port, debug=True)
