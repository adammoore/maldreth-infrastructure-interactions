"""
MaLDReTH Tool Interactions Blueprint

This blueprint can be integrated into existing Flask applications.
"""

from flask import Blueprint, render_template, jsonify, request
import sqlite3
from typing import Dict, List, Any

# Create blueprint
interactions_bp = Blueprint('interactions', __name__, 
                          template_folder='templates/interactions',
                          static_folder='static',
                          url_prefix='/interactions')

class InteractionsService:
    """Service class for tool interactions functionality."""
    
    def __init__(self, db_path: str = "maldreth_interactions.db"):
        self.db_path = db_path
    
    def get_db_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_interactions(self, filters: Dict[str, Any] = None):
        """Get all interactions with optional filtering."""
        query = """
            SELECT 
                i.*,
                s.name as source_tool_name,
                s.stage_id as source_stage_id,
                t.name as target_tool_name,
                t.stage_id as target_stage_id,
                ss.name as source_stage,
                ts.name as target_stage
            FROM interactions i
            JOIN tools s ON i.source_tool_id = s.id
            JOIN tools t ON i.target_tool_id = t.id
            JOIN lifecycle_stages ss ON s.stage_id = ss.id
            JOIN lifecycle_stages ts ON t.stage_id = ts.id
            WHERE 1=1
        """
        
        params = []
        if filters:
            if filters.get('stage'):
                query += " AND (ss.name = ? OR ts.name = ?)"
                params.extend([filters['stage'], filters['stage']])
            if filters.get('type'):
                query += " AND i.interaction_type = ?"
                params.append(filters['type'])
            if filters.get('complexity'):
                query += " AND i.complexity_level = ?"
                params.append(filters['complexity'])
        
        query += " ORDER BY i.created_at DESC"
        
        with self.get_db_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

# Initialize service
interactions_service = InteractionsService()

@interactions_bp.route('/')
def index():
    """Interactions dashboard."""
    interactions = interactions_service.get_all_interactions()
    return render_template('interactions/index.html', interactions=interactions)

@interactions_bp.route('/api/interactions')
def api_interactions():
    """API endpoint for interactions."""
    filters = {
        'stage': request.args.get('stage'),
        'type': request.args.get('type'),
        'complexity': request.args.get('complexity')
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v}
    
    interactions = interactions_service.get_all_interactions(filters)
    return jsonify(interactions)

@interactions_bp.route('/api/stats')
def api_stats():
    """API endpoint for statistics."""
    with interactions_service.get_db_connection() as conn:
        # Get basic counts
        cursor = conn.execute("SELECT COUNT(*) as count FROM interactions")
        total_interactions = cursor.fetchone()['count']
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM tools")
        total_tools = cursor.fetchone()['count']
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM lifecycle_stages")
        total_stages = cursor.fetchone()['count']
        
        # Get interaction types
        cursor = conn.execute("""
            SELECT interaction_type, COUNT(*) as count
            FROM interactions
            GROUP BY interaction_type
            ORDER BY count DESC
        """)
        interaction_types = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'total_interactions': total_interactions,
            'total_tools': total_tools,
            'total_stages': total_stages,
            'interaction_types': interaction_types
        })

def register_interactions_blueprint(app):
    """Register the interactions blueprint with a Flask app."""
    app.register_blueprint(interactions_bp)
    return app
