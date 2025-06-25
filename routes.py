"""
routes.py

API routes for MaLDReTH Infrastructure Interactions.
"""

from flask import Blueprint, jsonify, request, render_template
from models import db, Stage, ToolCategory, Tool, Connection

# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@main_bp.route('/api/lifecycle')
def get_lifecycle():
    """Get all lifecycle stages with connections."""
    try:
        stages = Stage.query.all()
        
        # Build nodes
        nodes = []
        for stage in stages:
            nodes.append({
                'id': stage.id,
                'name': stage.name,
                'description': stage.description
            })
        
        # Build connections
        connections = Connection.query.all()
        links = []
        for conn in connections:
            from_stage = Stage.query.get(conn.from_stage_id)
            to_stage = Stage.query.get(conn.to_stage_id)
            if from_stage and to_stage:
                links.append({
                    'from': from_stage.name,
                    'to': to_stage.name,
                    'type': conn.type
                })
        
        return jsonify({
            'nodes': nodes,
            'links': links
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/tools/<stage_name>')
def get_tools(stage_name):
    """Get tools for a specific stage."""
    try:
        # Find stage
        stage = Stage.query.filter_by(name=stage_name.upper()).first()
        if not stage:
            return jsonify([])
        
        # Get tools
        tools = Tool.query.filter_by(stage_id=stage.id).all()
        
        result = []
        for tool in tools:
            category = ToolCategory.query.get(tool.category_id)
            result.append({
                'id': tool.id,
                'name': tool.name,
                'description': tool.description,
                'link': tool.link,
                'provider': tool.provider,
                'category': category.category if category else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/search')
def search_tools():
    """Search for tools."""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    try:
        # Search in tool names and descriptions
        tools = Tool.query.filter(
            db.or_(
                Tool.name.ilike(f'%{query}%'),
                Tool.description.ilike(f'%{query}%')
            )
        ).all()
        
        result = []
        for tool in tools:
            category = ToolCategory.query.get(tool.category_id)
            stage = Stage.query.get(tool.stage_id)
            result.append({
                'id': tool.id,
                'name': tool.name,
                'description': tool.description,
                'link': tool.link,
                'provider': tool.provider,
                'category': category.category if category else None,
                'stage': stage.name if stage else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/health')
def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Get counts
        stages = Stage.query.count()
        categories = ToolCategory.query.count()
        tools = Tool.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'counts': {
                'stages': stages,
                'categories': categories,
                'tools': tools
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
