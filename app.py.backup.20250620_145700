"""
MaLDReTH Research Data Lifecycle Visualization Flask Application
Updated for Heroku deployment and compatibility with existing infrastructure

Based on RDA-OfR Working Group specifications and existing maldreth implementations
Author: Adam Vials Moore / Generated for MaLDReTH project
Version: 2.0.0
License: Apache 2.0
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Union, Optional
from flask import Flask, render_template, jsonify, request, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError
import sqlite3
from contextlib import closing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration for Heroku and local development
class Config:
    """Application configuration optimized for Heroku deployment"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'maldreth-dev-key-2024'
    
    # Database configuration - Heroku provides DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///maldreth.db'
    
    # Fix for Heroku Postgres URL
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Heroku configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.environ.get('PORT', 5000))

app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models based on MaLDReTH specification
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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
            'tools': [tool.name for tool in self.tools],  # Simplified for frontend compatibility
            'tool_count': self.tools.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<ToolCategory(name='{self.name}', stage='{self.stage.name if self.stage else 'None'}')>"

class ResearchTool(db.Model):
    """Model representing a research tool within the MaLDReTH framework"""
    __tablename__ = 'research_tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    provider = db.Column(db.String(200))
    tool_type = db.Column(db.String(100))
    source_type = db.Column(db.String(50), default='open')  # open, closed, mixed
    scope = db.Column(db.String(100))  # Generic, Disciplinary
    interoperable = db.Column(db.String(50), default='true')  # true, false, partial
    characteristics = db.Column(db.Text)  # Additional tool characteristics
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    
    def __repr__(self):
        return f"<ResearchTool(name='{self.name}', provider='{self.provider}')>"

class LifecycleConnection(db.Model):
    """Model representing connections between lifecycle stages"""
    __tablename__ = 'lifecycle_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    from_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    to_stage_id = db.Column(db.Integer, db.ForeignKey('lifecycle_stages.id'), nullable=False)
    connection_type = db.Column(db.String(50), default='normal')  # normal, alternative, bidirectional
    description = db.Column(db.Text)
    
    from_stage = db.relationship('LifecycleStage', foreign_keys=[from_stage_id])
    to_stage = db.relationship('LifecycleStage', foreign_keys=[to_stage_id])
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'from_stage_id': self.from_stage_id,
            'to_stage_id': self.to_stage_id,
            'from_stage_name': self.from_stage.name if self.from_stage else None,
            'to_stage_name': self.to_stage.name if self.to_stage else None,
            'connection_type': self.connection_type,
            'description': self.description
        }

# Routes
@app.route('/')
def index():
    """Serve the main curation interface"""
    return render_template('curation.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint for Heroku and monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    })

@app.route('/api/lifecycle-data')
def get_lifecycle_data():
    """Get all lifecycle data in the format expected by the frontend"""
    try:
        stages = LifecycleStage.query.order_by(LifecycleStage.order).all()
        
        # Format data for frontend compatibility
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

@app.route('/api/stages/<int:stage_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_single_stage(stage_id):
    """Get, update, or delete a specific stage"""
    try:
        stage = LifecycleStage.query.get_or_404(stage_id)
        
        if request.method == 'GET':
            return jsonify(stage.to_dict())
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            stage.name = data.get('name', stage.name)
            stage.description = data.get('description', stage.description)
            stage.order = data.get('order', stage.order)
            stage.updated_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Updated stage: {stage.name}")
            return jsonify(stage.to_dict())
        
        elif request.method == 'DELETE':
            stage_name = stage.name
            db.session.delete(stage)
            db.session.commit()
            logger.info(f"Deleted stage: {stage_name}")
            return '', 204
            
    except NotFound:
        return jsonify({'error': 'Stage not found'}), 404
    except Exception as e:
        logger.error(f"Error managing single stage: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to manage stage'}), 500

@app.route('/api/categories', methods=['GET', 'POST'])
def manage_categories():
    """Get all categories or create a new category"""
    try:
        if request.method == 'GET':
            categories = ToolCategory.query.join(LifecycleStage).order_by(LifecycleStage.order, ToolCategory.name).all()
            return jsonify([cat.to_dict() for cat in categories])
        
        elif request.method == 'POST':
            data = request.get_json()
            
            if not data or not data.get('name') or not data.get('stage_id'):
                return jsonify({'error': 'Category name and stage_id are required'}), 400
            
            category = ToolCategory(
                name=data['name'],
                description=data.get('description', ''),
                stage_id=data['stage_id']
            )
            
            db.session.add(category)
            db.session.commit()
            
            logger.info(f"Created new category: {category.name}")
            return jsonify(category.to_dict()), 201
            
    except Exception as e:
        logger.error(f"Error managing categories: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to manage categories'}), 500

@app.route('/api/tools', methods=['GET', 'POST'])
def manage_tools():
    """Get all tools or create a new tool"""
    try:
        if request.method == 'GET':
            # Get query parameters for filtering
            category_id = request.args.get('category_id', type=int)
            stage_id = request.args.get('stage_id', type=int)
            
            query = ResearchTool.query.join(ToolCategory).join(LifecycleStage)
            
            if category_id:
                query = query.filter(ResearchTool.category_id == category_id)
            elif stage_id:
                query = query.filter(LifecycleStage.id == stage_id)
            
            tools = query.order_by(LifecycleStage.order, ToolCategory.name, ResearchTool.name).all()
            return jsonify([tool.to_dict() for tool in tools])
        
        elif request.method == 'POST':
            data = request.get_json()
            
            if not data or not data.get('name') or not data.get('category_id'):
                return jsonify({'error': 'Tool name and category_id are required'}), 400
            
            tool = ResearchTool(
                name=data['name'],
                description=data.get('description', ''),
                url=data.get('url', ''),
                provider=data.get('provider', ''),
                tool_type=data.get('tool_type', ''),
                source_type=data.get('source_type', 'open'),
                scope=data.get('scope', 'Generic'),
                interoperable=data.get('interoperable', 'true'),
                characteristics=data.get('characteristics', ''),
                category_id=data['category_id']
            )
            
            db.session.add(tool)
            db.session.commit()
            
            logger.info(f"Created new tool: {tool.name}")
            return jsonify(tool.to_dict()), 201
            
    except Exception as e:
        logger.error(f"Error managing tools: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to manage tools'}), 500

@app.route('/api/export/<format>')
def export_data(format):
    """Export data in various formats"""
    try:
        if format not in ['json', 'csv']:
            return jsonify({'error': 'Unsupported format. Use json or csv'}), 400
        
        stages = LifecycleStage.query.order_by(LifecycleStage.order).all()
        
        if format == 'json':
            data = {
                'metadata': {
                    'exported_at': datetime.utcnow().isoformat(),
                    'version': '2.0.0',
                    'source': 'MaLDReTH Research Data Lifecycle'
                },
                'stages': [stage.to_dict() for stage in stages]
            }
            return jsonify(data)
        
        elif format == 'csv':
            # Create CSV data
            csv_data = []
            for stage in stages:
                for category in stage.tool_categories:
                    for tool in category.tools:
                        csv_data.append({
                            'Stage': stage.name,
                            'Stage_Order': stage.order,
                            'Category': category.name,
                            'Tool_Name': tool.name,
                            'Provider': tool.provider or '',
                            'URL': tool.url or '',
                            'Type': tool.tool_type or '',
                            'Source': tool.source_type,
                            'Scope': tool.scope,
                            'Interoperable': tool.interoperable,
                            'Description': tool.description or ''
                        })
            
            if not csv_data:
                return jsonify({'error': 'No data to export'}), 404
            
            # Convert to CSV
            df = pd.DataFrame(csv_data)
            csv_output = df.to_csv(index=False)
            
            from flask import Response
            return Response(
                csv_output,
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
            'total_connections': LifecycleConnection.query.count(),
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
            
            # MaLDReTH Lifecycle Stages as defined in the working group documents
            maldreth_stages = [
                {
                    'name': 'Conceptualise',
                    'description': 'To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.',
                    'order': 1
                },
                {
                    'name': 'Plan',
                    'description': 'To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis. Data management plans (DMP) should be established for this phase of the lifecycle.',
                    'order': 2
                },
                {
                    'name': 'Fund',
                    'description': 'To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.',
                    'order': 3
                },
                {
                    'name': 'Collect',
                    'description': 'To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.',
                    'order': 4
                },
                {
                    'name': 'Process',
                    'description': 'To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.',
                    'order': 5
                },
                {
                    'name': 'Analyse',
                    'description': 'To derive insights, knowledge, and understanding from processed data. Data analysis involves iterative exploration and interpretation of experimental or computational results.',
                    'order': 6
                },
                {
                    'name': 'Store',
                    'description': 'To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.',
                    'order': 7
                },
                {
                    'name': 'Publish',
                    'description': 'To release research data in published form for use by others with appropriate metadata for citation (including a unique persistent identifier) based on FAIR principles.',
                    'order': 8
                },
                {
                    'name': 'Preserve',
                    'description': 'To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.',
                    'order': 9
                },
                {
                    'name': 'Share',
                    'description': 'To make data available and accessible to humans and/or machines. Data may be shared with project collaborators or published to share it with the wider research community.',
                    'order': 10
                },
                {
                    'name': 'Access',
                    'description': 'To control and manage data access by designated users and reusers. This may be in the form of publicly available published information.',
                    'order': 11
                },
                {
                    'name': 'Transform',
                    'description': 'To create new data from the original, for example: by migration into a different format; by creating a subset; or combining with other data.',
                    'order': 12
                }
            ]
            
            # Create stages
            stage_objects = {}
            for stage_data in maldreth_stages:
                stage = LifecycleStage(**stage_data)
                db.session.add(stage)
                db.session.flush()  # To get the ID
                stage_objects[stage.name] = stage
            
            # Sample categories and tools based on the CSV data provided
            sample_data = [
                {
                    'stage': 'Conceptualise',
                    'categories': [
                        {
                            'name': 'Mind mapping, concept mapping and knowledge modelling',
                            'description': 'Tools that define the entities of research and their relationships',
                            'tools': ['Miro', 'Meister Labs (MindMeister + MeisterTask)', 'XMind']
                        },
                        {
                            'name': 'Diagramming and flowchart',
                            'description': 'Tools that detail the research workflow',
                            'tools': ['Lucidchart', 'Draw.io (now Diagrams.net)', 'Creately']
                        },
                        {
                            'name': 'Wireframing and prototyping',
                            'description': 'Tools that visualise and demonstrate the research workflow',
                            'tools': ['Balsamiq', 'Figma']
                        }
                    ]
                },
                {
                    'stage': 'Plan',
                    'categories': [
                        {
                            'name': 'Data management planning (DMP)',
                            'description': 'Tools focused on enabling preparation and submission of data management plans',
                            'tools': ['DMP Tool', 'DMP Online', 'RDMO']
                        },
                        {
                            'name': 'Project planning',
                            'description': 'Tools designed to enable project planning',
                            'tools': ['Trello', 'Asana', 'Microsoft Project']
                        }
                    ]
                },
                {
                    'stage': 'Collect',
                    'categories': [
                        {
                            'name': 'Quantitative data collection tool',
                            'description': 'Tools that collect quantitative data',
                            'tools': ['Open Data Kit', 'GBIF', 'Cedar WorkBench']
                        },
                        {
                            'name': 'Qualitative data collection (e.g. Survey tool)',
                            'description': 'Tools that collect qualitative data',
                            'tools': ['Survey Monkey', 'Online Surveys', 'Zooniverse']
                        }
                    ]
                }
            ]
            
            # Create categories and tools
            for stage_data in sample_data:
                stage = stage_objects[stage_data['stage']]
                
                for cat_data in stage_data['categories']:
                    category = ToolCategory(
                        name=cat_data['name'],
                        description=cat_data['description'],
                        stage_id=stage.id
                    )
                    db.session.add(category)
                    db.session.flush()
                    
                    for tool_name in cat_data['tools']:
                        tool = ResearchTool(
                            name=tool_name,
                            category_id=category.id,
                            source_type='open',
                            scope='Generic',
                            interoperable='true'
                        )
                        db.session.add(tool)
            
            # Create basic connections
            connections = [
                (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), 
                (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 1)
            ]
            
            for from_order, to_order in connections:
                from_stage = LifecycleStage.query.filter_by(order=from_order).first()
                to_stage = LifecycleStage.query.filter_by(order=to_order).first()
                
                if from_stage and to_stage:
                    connection = LifecycleConnection(
                        from_stage_id=from_stage.id,
                        to_stage_id=to_stage.id,
                        connection_type='normal'
                    )
                    db.session.add(connection)
            
            db.session.commit()
            logger.info("MaLDReTH data initialization completed successfully")
            
    except Exception as e:
        logger.error(f"Error initializing MaLDReTH data: {e}")
        db.session.rollback()
        raise

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Heroku requires the application to be callable
def create_app():
    """Application factory for Heroku deployment"""
    return app

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
