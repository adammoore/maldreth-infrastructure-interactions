#!/bin/bash
# MaLDReTH Heroku Deployment Hotfix
# Run this script to immediately fix the pandas/numpy crash issue

echo "🔧 MaLDReTH Heroku Deployment Hotfix"
echo "===================================="

# Step 1: Update requirements.txt to remove pandas
echo "Step 1: Updating requirements.txt..."
cat > requirements.txt << 'EOF'
# MaLDReTH Infrastructure Interactions - Heroku Optimized
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-CORS==4.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.7
SQLAlchemy==2.0.21
Werkzeug==2.3.7
Jinja2==3.1.2
python-dotenv==1.0.0
python-dateutil==2.8.2
marshmallow==3.20.1
click>=8.0
itsdangerous>=2.0
MarkupSafe>=2.0
six==1.16.0
EOF

# Step 2: Backup current app.py if it exists
if [ -f "app.py" ]; then
    echo "Step 2: Backing up current app.py..."
    cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)
fi

# Step 3: Check if templates directory exists
echo "Step 3: Checking template structure..."
if [ ! -d "templates" ]; then
    mkdir -p templates
    echo "Created templates directory"
fi

# Step 4: Create minimal working app.py (the simplified version from artifacts)
echo "Step 4: Creating optimized app.py..."
# (The simplified app.py content would go here - use the artifact content)
cat > app.py << 'EOF'
"""
MaLDReTH Research Data Lifecycle Infrastructure Interactions
Simplified version without pandas dependency for Heroku stability

Author: Adam Vials Moore
Version: 2.1.0 (Heroku-optimized)
License: Apache 2.0
"""

import os
import json
import logging
import csv
import io
from datetime import datetime
from typing import Dict, List, Union, Optional
from flask import Flask, render_template, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration for Heroku
class Config:
    """Application configuration optimized for Heroku deployment"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'maldreth-infrastructure-key-2024'
    
    # Database configuration - Heroku provides DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///maldreth.db'
    
    # Fix for Heroku Postgres URL format change
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.environ.get('PORT', 5000))

app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models
class LifecycleStage(db.Model):
    """Model representing a stage in the MaLDReTH research data lifecycle"""
    __tablename__ = 'lifecycle_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tool_categories = db.relationship('ToolCategory', backref='stage', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict:
        """Convert model instance to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'order': self.order,
            'categories': [cat.to_dict() for cat in self.tool_categories],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<LifecycleStage(name='{self.name}', order={self.order})>"

class ToolCategory(db.Model):
    """Model representing a tool category within a lifecycle stage"""
    __tablename__ = 'tool_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tools = db.relationship('ResearchTool', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict:
        """Convert model instance to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stage_id': self.stage_id,
            'stage_name': self.stage.name if self.stage else None,
            'tools': [tool.name for tool in self.tools],
            'tool_count': self.tools.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ResearchTool(db.Model):
    """Model representing a research tool within the MaLDReTH framework"""
    __tablename__ = 'research_tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    provider = db.Column(db.String(200))
    tool_type = db.Column(db.String(100))
    source_type = db.Column(db.String(50), default='open')
    scope = db.Column(db.String(100), default='Generic')
    interoperable = db.Column(db.String(50), default='true')
    characteristics = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convert model instance to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'provider': self.provider,
            'tool_type': self.tool_type,
            'source_type': self.source_type,
            'scope': self.scope,
            'interoperable': self.interoperable,
            'characteristics': self.characteristics,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'stage_name': self.category.stage.name if self.category and self.category.stage else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class InfrastructureInteraction(db.Model):
    """Model for tracking infrastructure interactions"""
    __tablename__ = 'infrastructure_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    interaction_type = db.Column(db.String(100), nullable=False)
    source_system = db.Column(db.String(100))
    target_system = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')
    lifecycle_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'interaction_type': self.interaction_type,
            'source_system': self.source_system,
            'target_system': self.target_system,
            'description': self.description,
            'status': self.status,
            'lifecycle_stage_id': self.lifecycle_stage_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Routes
@app.route('/')
def index():
    """Main index page"""
    return render_template('index.html')

@app.route('/curator')
def curator():
    """Main curation interface"""
    return render_template('curator.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint for Heroku and monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.1.0'
    })

@app.route('/api/lifecycle-data')
def get_lifecycle_data():
    """Get all lifecycle data in the format expected by the frontend"""
    try:
        stages = LifecycleStage.query.order_by(LifecycleStage.order).all()
        
        data = {
            'stages': [stage.to_dict() for stage in stages],
            'total_stages': len(stages),
            'total_categories': sum(stage.tool_categories.count() for stage in stages),
            'total_tools': ResearchTool.query.count(),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching lifecycle data: {e}")
        return jsonify({'error': 'Failed to fetch lifecycle data'}), 500

@app.route('/api/stages', methods=['GET', 'POST'])
def manage_stages():
    """Get all stages or create a new stage"""
    try:
        if request.method == 'GET':
            stages = LifecycleStage.query.order_by(LifecycleStage.order).all()
            return jsonify([stage.to_dict() for stage in stages])
        
        elif request.method == 'POST':
            data = request.get_json()
            
            if not data or not data.get('name'):
                return jsonify({'error': 'Stage name is required'}), 400
            
            stage = LifecycleStage(
                name=data['name'],
                description=data.get('description', ''),
                order=data.get('order', LifecycleStage.query.count() + 1)
            )
            
            db.session.add(stage)
            db.session.commit()
            
            logger.info(f"Created new stage: {stage.name}")
            return jsonify(stage.to_dict()), 201
            
    except Exception as e:
        logger.error(f"Error managing stages: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to manage stages'}), 500

@app.route('/api/export/<format>')
def export_data(format):
    """Export data in various formats without pandas dependency"""
    try:
        if format not in ['json', 'csv']:
            return jsonify({'error': 'Unsupported format. Use json or csv'}), 400
        
        stages = LifecycleStage.query.order_by(LifecycleStage.order).all()
        
        if format == 'json':
            data = {
                'metadata': {
                    'exported_at': datetime.utcnow().isoformat(),
                    'version': '2.1.0',
                    'source': 'MaLDReTH Infrastructure Interactions'
                },
                'stages': [stage.to_dict() for stage in stages]
            }
            return jsonify(data)
        
        elif format == 'csv':
            # Create CSV data using standard library
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow([
                'Stage', 'Stage_Order', 'Category', 'Tool_Name', 
                'Provider', 'URL', 'Type', 'Source', 'Scope', 'Interoperable'
            ])
            
            # Write data
            for stage in stages:
                for category in stage.tool_categories:
                    for tool in category.tools:
                        writer.writerow([
                            stage.name,
                            stage.order,
                            category.name,
                            tool.name,
                            tool.provider or '',
                            tool.url or '',
                            tool.tool_type or '',
                            tool.source_type,
                            tool.scope,
                            tool.interoperable
                        ])
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=maldreth_data.csv'}
            )
            
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({'error': 'Failed to export data'}), 500

@app.route('/api/statistics')
def get_statistics():
    """Get application statistics for dashboard"""
    try:
        stats = {
            'total_stages': LifecycleStage.query.count(),
            'total_categories': ToolCategory.query.count(),
            'total_tools': ResearchTool.query.count(),
            'total_interactions': InfrastructureInteraction.query.count(),
            'last_updated': datetime.utcnow().isoformat(),
            'by_stage': {}
        }
        
        # Get detailed stats by stage
        stages = LifecycleStage.query.order_by(LifecycleStage.order).all()
        for stage in stages:
            stats['by_stage'][stage.name] = {
                'categories': stage.tool_categories.count(),
                'tools': sum(cat.tools.count() for cat in stage.tool_categories)
            }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500

def init_maldreth_data():
    """Initialize database with MaLDReTH lifecycle data"""
    try:
        if LifecycleStage.query.count() == 0:
            logger.info("Initializing MaLDReTH data...")
            
            # MaLDReTH Lifecycle Stages
            maldreth_stages = [
                {
                    'name': 'Conceptualise',
                    'description': 'To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.',
                    'order': 1
                },
                {
                    'name': 'Plan',
                    'description': 'To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis.',
                    'order': 2
                },
                {
                    'name': 'Collect',
                    'description': 'To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.',
                    'order': 3
                }
            ]
            
            # Create stages and sample data
            for stage_data in maldreth_stages:
                stage = LifecycleStage(**stage_data)
                db.session.add(stage)
                db.session.flush()
                
                # Add sample category for each stage
                category = ToolCategory(
                    name=f"{stage.name} Tools",
                    description=f"Tools for the {stage.name} stage",
                    stage_id=stage.id
                )
                db.session.add(category)
                db.session.flush()
                
                # Add sample tool
                tool = ResearchTool(
                    name=f"Sample {stage.name} Tool",
                    description=f"A tool for {stage.name.lower()} activities",
                    category_id=category.id
                )
                db.session.add(tool)
            
            db.session.commit()
            logger.info("MaLDReTH data initialization completed")
            
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        db.session.rollback()
        raise

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create database tables and initialize data
    with app.app_context():
        try:
            db.create_all()
            init_maldreth_data()
            logger.info("Application started successfully")
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            raise
    
    # Run the application
    app.run(
        host='0.0.0.0', 
        port=app.config['PORT'], 
        debug=app.config['DEBUG']
    )
EOF


# Step 5: Ensure Procfile is correct
echo "Step 5: Updating Procfile..."
echo "web: gunicorn app:app --bind 0.0.0.0:\$PORT --workers=2 --timeout=120" > Procfile

# Step 6: Update runtime.txt
echo "Step 6: Updating runtime.txt..."
echo "python-3.11.6" > runtime.txt

# Step 7: Commit and push changes
echo "Step 7: Committing changes..."
git add requirements.txt app.py Procfile runtime.txt
git commit -m "hotfix: remove pandas dependency causing Heroku crashes

- Remove pandas and numpy dependencies that cause binary incompatibility
- Simplify app.py to use standard library for CSV export
- Optimize requirements.txt for Heroku deployment
- Fix numpy.dtype size mismatch error"

echo "Step 8: Pushing to Heroku..."
git push heroku main

echo ""
echo "✅ Hotfix deployment complete!"
echo ""
echo "🔍 Monitor deployment:"
echo "  heroku logs --tail -a your-app-name"
echo ""
echo "🌐 Test endpoints:"
echo "  curl https://your-app-name.herokuapp.com/api/health"
echo "  curl https://your-app-name.herokuapp.com/"
echo ""
echo "📊 If successful, the app should now start without pandas errors."
