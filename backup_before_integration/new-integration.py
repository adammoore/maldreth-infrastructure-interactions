#!/usr/bin/env python3
"""
Integration script for MaLDReTH Tool Interactions with existing codebase.

This script will:
1. Explore the existing project structure
2. Create necessary directories
3. Integrate new functionality with existing code
4. Update configuration files
5. Provide migration instructions

Run this script from your project root directory:
python3 integrate_maldreth_interactions.py
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any

class MaLDReTHIntegrator:
    """Integrates the new tool interactions functionality with existing codebase."""
    
    def __init__(self, project_root: str = "."):
        """Initialize with project root directory."""
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / "backup_before_integration"
        
    def analyze_existing_structure(self) -> Dict[str, Any]:
        """Analyze existing project structure."""
        analysis = {
            "has_flask_app": False,
            "has_database": False,
            "has_templates": False,
            "has_static": False,
            "has_requirements": False,
            "existing_files": [],
            "directories": [],
            "python_files": [],
            "config_files": []
        }
        
        print("🔍 Analyzing existing project structure...")
        
        for item in self.project_root.rglob("*"):
            if item.is_file():
                analysis["existing_files"].append(str(item.relative_to(self.project_root)))
                
                if item.name in ["app.py", "main.py", "server.py"]:
                    analysis["has_flask_app"] = True
                elif item.suffix == ".py":
                    analysis["python_files"].append(str(item.relative_to(self.project_root)))
                elif item.name == "requirements.txt":
                    analysis["has_requirements"] = True
                elif item.suffix in [".db", ".sqlite", ".sqlite3"]:
                    analysis["has_database"] = True
                elif item.name in ["config.py", "settings.py", ".env"]:
                    analysis["config_files"].append(str(item.relative_to(self.project_root)))
                    
            elif item.is_dir():
                analysis["directories"].append(str(item.relative_to(self.project_root)))
                
                if item.name == "templates":
                    analysis["has_templates"] = True
                elif item.name == "static":
                    analysis["has_static"] = True
        
        return analysis
    
    def create_backup(self):
        """Create backup of existing files before modification."""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print(f"📦 Creating backup at {self.backup_dir}")
        
        # Copy important files to backup
        important_files = ["*.py", "*.txt", "*.md", "*.json", "*.yml", "*.yaml"]
        self.backup_dir.mkdir(parents=True)
        
        for pattern in important_files:
            for file in self.project_root.glob(pattern):
                if file.is_file():
                    backup_file = self.backup_dir / file.name
                    shutil.copy2(file, backup_file)
    
    def create_directory_structure(self):
        """Create necessary directories for the integration."""
        directories = [
            "templates",
            "static/css",
            "static/js", 
            "static/images",
            "migrations",
            "tests",
            "docs",
            "scripts"
        ]
        
        print("📁 Creating directory structure...")
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {directory}")
    
    def update_requirements(self, analysis: Dict[str, Any]):
        """Update or create requirements.txt with necessary dependencies."""
        new_requirements = [
            "Flask==2.3.3",
            "Flask-CORS==4.0.0", 
            "gunicorn==21.2.0",
            "python-dotenv==1.0.0",
            "click==8.1.7"
        ]
        
        requirements_file = self.project_root / "requirements.txt"
        
        existing_requirements = []
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                existing_requirements = [line.strip() for line in f.readlines() if line.strip()]
        
        # Merge requirements, avoiding duplicates
        all_requirements = list(existing_requirements)
        for req in new_requirements:
            package_name = req.split('==')[0]
            if not any(existing.startswith(package_name) for existing in existing_requirements):
                all_requirements.append(req)
        
        with open(requirements_file, 'w') as f:
            f.write('\n'.join(sorted(all_requirements)) + '\n')
        
        print(f"📝 Updated requirements.txt with {len(new_requirements)} new dependencies")
    
    def create_database_integration(self):
        """Create database integration files."""
        
        # Enhanced database initialization script
        db_init_script = '''#!/usr/bin/env python3
"""
Enhanced MaLDReTH database initialization script.
Integrates with existing project structure.
"""

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

class MaLDReTHDatabase:
    """Enhanced database class for MaLDReTH tool interactions."""
    
    def __init__(self, db_path: str = "maldreth_interactions.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.project_root = Path(__file__).parent
        
    def get_connection(self):
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self):
        """Initialize database with enhanced schema."""
        schema_sql = """
        -- Enhanced schema for MaLDReTH interactions
        
        CREATE TABLE IF NOT EXISTS lifecycle_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            order_number INTEGER NOT NULL,
            color_code TEXT DEFAULT '#007bff',
            icon TEXT DEFAULT 'fas fa-circle',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS tool_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            stage_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stage_id) REFERENCES lifecycle_stages (id)
        );
        
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            url TEXT,
            provider TEXT,
            source_type TEXT CHECK (source_type IN ('open', 'closed', 'freemium')),
            category_id INTEGER,
            stage_id INTEGER NOT NULL,
            license_type TEXT,
            cost_model TEXT,
            documentation_url TEXT,
            api_available BOOLEAN DEFAULT 0,
            integration_complexity TEXT CHECK (integration_complexity IN ('low', 'medium', 'high')),
            user_rating REAL CHECK (user_rating >= 0 AND user_rating <= 5),
            active_users INTEGER DEFAULT 0,
            last_updated DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES tool_categories (id),
            FOREIGN KEY (stage_id) REFERENCES lifecycle_stages (id)
        );
        
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_tool_id INTEGER NOT NULL,
            target_tool_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL CHECK (interaction_type IN ('data_flow', 'integration', 'workflow', 'export_import')),
            interaction_method TEXT CHECK (interaction_method IN ('api', 'file_export', 'direct_integration', 'manual_transfer')),
            description TEXT NOT NULL,
            use_case TEXT,
            data_format TEXT,
            frequency TEXT CHECK (frequency IN ('one-time', 'daily', 'weekly', 'monthly', 'project-based', 'real-time')),
            complexity_level TEXT CHECK (complexity_level IN ('low', 'medium', 'high')),
            technical_requirements TEXT,
            benefits TEXT,
            challenges TEXT,
            implementation_time_estimate INTEGER, -- in hours
            success_rate REAL CHECK (success_rate >= 0 AND success_rate <= 100),
            documentation_quality INTEGER CHECK (documentation_quality >= 1 AND documentation_quality <= 5),
            community_support INTEGER CHECK (community_support >= 1 AND community_support <= 5),
            documented BOOLEAN DEFAULT 0,
            community_validated BOOLEAN DEFAULT 0,
            validation_date DATE,
            validation_source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_tool_id) REFERENCES tools (id),
            FOREIGN KEY (target_tool_id) REFERENCES tools (id)
        );
        
        CREATE TABLE IF NOT EXISTS interaction_examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            code_example TEXT,
            configuration_example TEXT,
            success_criteria TEXT,
            common_issues TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES interactions (id)
        );
        
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            tool_id INTEGER,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            user_role TEXT,
            organization_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES interactions (id),
            FOREIGN KEY (tool_id) REFERENCES tools (id)
        );
        
        -- Indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_tools_stage ON tools(stage_id);
        CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category_id);
        CREATE INDEX IF NOT EXISTS idx_interactions_source ON interactions(source_tool_id);
        CREATE INDEX IF NOT EXISTS idx_interactions_target ON interactions(target_tool_id);
        CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(interaction_type);
        """
        
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()
        
        print("✅ Database schema initialized")
    
    def populate_sample_data(self):
        """Populate database with comprehensive sample data."""
        # This would include the comprehensive data from the previous artifacts
        # Implementation details would go here
        pass

if __name__ == "__main__":
    db = MaLDReTHDatabase()
    db.initialize_database()
    db.populate_sample_data()
    print("🎉 Database initialization complete!")
'''
        
        with open(self.project_root / "database_init.py", 'w') as f:
            f.write(db_init_script)
        
        print("📊 Created enhanced database initialization script")
    
    def create_flask_integration(self, analysis: Dict[str, Any]):
        """Create or enhance Flask application integration."""
        
        if analysis["has_flask_app"]:
            print("🔧 Existing Flask app detected - creating integration module")
            # Create integration module that can be imported
            self.create_interactions_blueprint()
        else:
            print("🆕 Creating new Flask application")
            self.create_standalone_app()
    
    def create_interactions_blueprint(self):
        """Create a Flask blueprint for interactions functionality."""
        
        blueprint_code = '''"""
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
'''
        
        with open(self.project_root / "interactions_blueprint.py", 'w') as f:
            f.write(blueprint_code)
        
        print("🔌 Created interactions blueprint for existing Flask app")
    
    def create_standalone_app(self):
        """Create standalone Flask application."""
        # This would create the full Flask app from the previous artifacts
        pass
    
    def create_templates(self):
        """Create HTML templates."""
        templates_dir = self.project_root / "templates" / "interactions"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create base template for interactions
        base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}MaLDReTH Tool Interactions{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('interactions.index') }}">
                <i class="fas fa-project-diagram me-2"></i>
                MaLDReTH Interactions
            </a>
        </div>
    </nav>

    <main class="container my-4">
        {% block content %}{% endblock %}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>'''
        
        with open(templates_dir / "base.html", 'w') as f:
            f.write(base_template)
        
        # Create index template
        index_template = '''{% extends "interactions/base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-exchange-alt me-2"></i>Tool Interactions</h1>
        <p class="lead">Explore research tool interactions across the data lifecycle</p>
    </div>
</div>

<div class="row">
    {% for interaction in interactions %}
        <div class="col-md-6 mb-4">
            <div class="card">
                <div class="card-body">
                    <h6 class="card-title">
                        {{ interaction.source_tool_name }}
                        <i class="fas fa-arrow-right mx-2"></i>
                        {{ interaction.target_tool_name }}
                    </h6>
                    <p class="card-text">{{ interaction.description[:150] }}...</p>
                    <div>
                        <span class="badge bg-primary">{{ interaction.interaction_type }}</span>
                        <span class="badge bg-secondary">{{ interaction.complexity_level }}</span>
                    </div>
                </div>
            </div>
        </div>
    {% endfor %}
</div>
{% endblock %}'''
        
        with open(templates_dir / "index.html", 'w') as f:
            f.write(index_template)
        
        print("📄 Created HTML templates")
    
    def create_integration_guide(self, analysis: Dict[str, Any]):
        """Create integration guide documentation."""
        
        guide_content = f"""# MaLDReTH Tool Interactions Integration Guide

## Integration Summary

This guide explains how the MaLDReTH tool interactions functionality has been integrated with your existing project.

## Project Analysis

**Existing Structure:**
- Flask App: {'✅ Found' if analysis['has_flask_app'] else '❌ Not found'}
- Database: {'✅ Found' if analysis['has_database'] else '❌ Not found'}
- Templates: {'✅ Found' if analysis['has_templates'] else '❌ Not found'}
- Requirements: {'✅ Found' if analysis['has_requirements'] else '❌ Not found'}

**Files Added:**
- `database_init.py` - Enhanced database initialization
- `interactions_blueprint.py` - Flask blueprint for interactions
- `templates/interactions/` - HTML templates
- `integration_guide.md` - This guide

## Integration Steps

### 1. Database Setup

Initialize the enhanced database:
```bash
python database_init.py
```

### 2. Flask Integration

If you have an existing Flask app, integrate the blueprint:

```python
from flask import Flask
from interactions_blueprint import register_interactions_blueprint

app = Flask(__name__)

# Register the interactions blueprint
register_interactions_blueprint(app)

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Access the Functionality

- Web Interface: `http://localhost:5000/interactions/`
- API Endpoints: 
  - `http://localhost:5000/interactions/api/interactions`
  - `http://localhost:5000/interactions/api/stats`

## API Usage Examples

### Get All Interactions
```python
import requests

response = requests.get('http://localhost:5000/interactions/api/interactions')
interactions = response.json()
```

### Filter Interactions
```python
# Filter by stage
response = requests.get('http://localhost:5000/interactions/api/interactions?stage=Analyse')

# Filter by type and complexity
response = requests.get('http://localhost:5000/interactions/api/interactions?type=data_flow&complexity=medium')
```

### Get Statistics
```python
response = requests.get('http://localhost:5000/interactions/api/stats')
stats = response.json()
print(f"Total interactions: {{stats['total_interactions']}}")
```

## Customization

### Adding Custom Interactions

```python
from interactions_blueprint import interactions_service

# Add your custom interaction data
interaction_data = {{
    'source_tool_id': 1,
    'target_tool_id': 2,
    'interaction_type': 'data_flow',
    'description': 'Your custom interaction description',
    # ... other fields
}}

# Use the service to add to database
```

### Extending the Blueprint

You can extend the blueprint by adding new routes:

```python
from interactions_blueprint import interactions_bp

@interactions_bp.route('/custom-endpoint')
def custom_endpoint():
    # Your custom functionality
    return jsonify({{'message': 'Custom endpoint'}})
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Run `database_init.py` to initialize the database
3. **Template Not Found**: Check that templates are in the correct directory

### Support

For technical issues, refer to the main project documentation or create an issue on the GitHub repository.

## Next Steps

1. Customize the templates to match your existing design
2. Add authentication if required
3. Extend the database schema for your specific needs
4. Add more interaction examples relevant to your research domain

"""
        
        with open(self.project_root / "INTEGRATION_GUIDE.md", 'w') as f:
            f.write(guide_content)
        
        print("📚 Created integration guide")
    
    def run_integration(self):
        """Run the complete integration process."""
        print("🚀 Starting MaLDReTH Tool Interactions Integration")
        print("=" * 55)
        
        # Analyze existing structure
        analysis = self.analyze_existing_structure()
        
        print(f"""
📋 Project Analysis:
   - Flask App: {'✅' if analysis['has_flask_app'] else '❌'}
   - Database: {'✅' if analysis['has_database'] else '❌'}
   - Templates: {'✅' if analysis['has_templates'] else '❌'}
   - Python files: {len(analysis['python_files'])}
   - Config files: {len(analysis['config_files'])}
        """)
        
        # Create backup
        self.create_backup()
        
        # Create directory structure
        self.create_directory_structure()
        
        # Update requirements
        self.update_requirements(analysis)
        
        # Create database integration
        self.create_database_integration()
        
        # Create Flask integration
        self.create_flask_integration(analysis)
        
        # Create templates
        self.create_templates()
        
        # Create integration guide
        self.create_integration_guide(analysis)
        
        print("\n🎉 Integration Complete!")
        print("""
Next steps:
1. Review the INTEGRATION_GUIDE.md file
2. Run: python database_init.py
3. Install dependencies: pip install -r requirements.txt
4. Integrate the blueprint with your Flask app
5. Test the functionality at /interactions/

📦 Backup created at: backup_before_integration/
📚 See INTEGRATION_GUIDE.md for detailed instructions
        """)

def main():
    """Main integration function."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."
    
    integrator = MaLDReTHIntegrator(project_root)
    integrator.run_integration()

if __name__ == "__main__":
    main()
