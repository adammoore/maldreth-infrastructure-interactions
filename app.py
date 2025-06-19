import logging
import logging.config
import sqlite3
import json
import os
from typing import Dict, List, Union, Optional, Tuple, Any
from contextlib import closing
from flask import Flask, render_template, jsonify, request
from datetime import datetime

# Configuration
DATABASE_CONFIG = {
    'DATABASE': 'maldreth_infrastructure.db',
    'SQLITE_URI': 'sqlite:///maldreth_infrastructure.db',
    'DEBUG': True,
    'SECRET_KEY': 'your_secret_key_here'
}

APP_CONFIG = {
    'HOST': '0.0.0.0',
    'PORT': 5000,
    'DEBUG': False
}

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(DATABASE_CONFIG)

# Database functions
def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_CONFIG['DATABASE'])
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def init_db() -> None:
    """Initialize the database with enhanced schema for infrastructure interactions."""
    try:
        with closing(get_db_connection()) as db:
            db.cursor().executescript('''
                -- Core tables from original schema
                DROP TABLE IF EXISTS stages;
                DROP TABLE IF EXISTS tool_categories;
                DROP TABLE IF EXISTS tools;
                DROP TABLE IF EXISTS connections;
                DROP TABLE IF EXISTS tool_metadata;
                DROP TABLE IF EXISTS infrastructure_interactions;
                DROP TABLE IF EXISTS curation_log;
                DROP TABLE IF EXISTS tool_characteristics;

                CREATE TABLE stages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    x INTEGER,
                    y INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE tool_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stage_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(stage_id) REFERENCES stages(id) ON DELETE CASCADE
                );

                CREATE TABLE tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    url TEXT,
                    provider TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(category_id) REFERENCES tool_categories(id) ON DELETE CASCADE
                );

                -- Enhanced metadata for tools
                CREATE TABLE tool_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_id INTEGER NOT NULL,
                    source_type TEXT CHECK(source_type IN ('open', 'closed', 'freemium')),
                    scope TEXT CHECK(scope IN ('generic', 'disciplinary', 'domain-specific')),
                    interoperable BOOLEAN DEFAULT 0,
                    api_available BOOLEAN DEFAULT 0,
                    data_formats TEXT, -- JSON array of supported formats
                    standards_compliant TEXT, -- JSON array of standards
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(tool_id) REFERENCES tools(id) ON DELETE CASCADE
                );

                -- Tool characteristics based on WG findings
                CREATE TABLE tool_characteristics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_id INTEGER NOT NULL,
                    characteristic_type TEXT NOT NULL,
                    characteristic_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(tool_id) REFERENCES tools(id) ON DELETE CASCADE
                );

                CREATE TABLE connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    view_mode TEXT NOT NULL,
                    from_stage TEXT NOT NULL,
                    to_stage TEXT NOT NULL,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- New table for infrastructure interactions
                CREATE TABLE infrastructure_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_tool_id INTEGER NOT NULL,
                    to_tool_id INTEGER NOT NULL,
                    interaction_type TEXT NOT NULL,
                    interaction_description TEXT,
                    data_flow_direction TEXT CHECK(data_flow_direction IN ('unidirectional', 'bidirectional')),
                    integration_method TEXT,
                    authentication_required BOOLEAN DEFAULT 0,
                    verified BOOLEAN DEFAULT 0,
                    verified_by TEXT,
                    verified_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(from_tool_id) REFERENCES tools(id) ON DELETE CASCADE,
                    FOREIGN KEY(to_tool_id) REFERENCES tools(id) ON DELETE CASCADE
                );

                -- Curation and maintenance log
                CREATE TABLE curation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    entity_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    curator_name TEXT,
                    curator_email TEXT,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Create indexes for better performance
                CREATE INDEX idx_tools_category ON tools(category_id);
                CREATE INDEX idx_tool_metadata_tool ON tool_metadata(tool_id);
                CREATE INDEX idx_interactions_from ON infrastructure_interactions(from_tool_id);
                CREATE INDEX idx_interactions_to ON infrastructure_interactions(to_tool_id);
                CREATE INDEX idx_curation_entity ON curation_log(entity_type, entity_id);

                -- Triggers to update timestamps
                CREATE TRIGGER update_stages_timestamp 
                AFTER UPDATE ON stages
                BEGIN
                    UPDATE stages SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;

                CREATE TRIGGER update_tool_categories_timestamp 
                AFTER UPDATE ON tool_categories
                BEGIN
                    UPDATE tool_categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;

                CREATE TRIGGER update_tools_timestamp 
                AFTER UPDATE ON tools
                BEGIN
                    UPDATE tools SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;

                CREATE TRIGGER update_tool_metadata_timestamp 
                AFTER UPDATE ON tool_metadata
                BEGIN
                    UPDATE tool_metadata SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;

                CREATE TRIGGER update_infrastructure_interactions_timestamp 
                AFTER UPDATE ON infrastructure_interactions
                BEGIN
                    UPDATE infrastructure_interactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;
            ''')
            db.commit()
        logger.info("Database initialized successfully with enhanced schema.")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        raise

def query_db(query: str, args: Tuple = (), one: bool = False) -> Optional[Any]:
    """Execute a database query and return the results."""
    try:
        with closing(get_db_connection()) as db:
            cur = db.execute(query, args)
            rv = cur.fetchall()
            return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        logger.error(f"Error executing query: {e}")
        return None

def insert_db(query: str, args: Tuple = ()) -> int:
    """Execute an insert query and return the last row id."""
    try:
        with closing(get_db_connection()) as db:
            cur = db.cursor()
            cur.execute(query, args)
            db.commit()
            return cur.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error executing insert: {e}")
        raise

def populate_db() -> None:
    """Populate the database with MaLDReTH data including enhanced tool information."""
    try:
        with closing(get_db_connection()) as db:
            cursor = db.cursor()

            # Define stages with descriptions
            stages_data = [
                ('CONCEPTUALISE', 'To formulate the initial research idea or hypothesis, and define the scope of the research project and the data component/requirements of that project.', 600, 100),
                ('PLAN', 'To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resources required for data collection, management and analysis.', 800, 200),
                ('FUND', 'To identify and acquire financial resources to support the research project, including data collection, management, analysis, sharing, publishing and preservation.', 900, 400),
                ('COLLECT', 'To use predefined procedures, methodologies and instruments to acquire and store data that is reliable, fit for purpose and of sufficient quality to test the research hypothesis.', 900, 600),
                ('PROCESS', 'To make new and existing data analysis-ready. This may involve standardised pre-processing, cleaning, reformatting, structuring, filtering, and performing quality control checks on data.', 800, 800),
                ('ANALYSE', 'To derive insights, knowledge, and understanding from processed data.', 600, 900),
                ('STORE', 'To record data using technological media appropriate for processing and analysis whilst maintaining data integrity and security.', 400, 900),
                ('PUBLISH', 'To release research data in published form for use by others with appropriate metadata for citation based on FAIR principles.', 200, 800),
                ('PRESERVE', 'To ensure the safety, integrity, and accessibility of data for as long as necessary so that data is as FAIR as possible.', 100, 600),
                ('SHARE', 'To make data available and accessible to humans and/or machines.', 100, 400),
                ('ACCESS', 'To control and manage data access by designated users and reusers.', 200, 200),
                ('TRANSFORM', 'To create new data from the original, for example by migration into a different format.', 400, 100)
            ]

            # Insert stages
            for name, desc, x, y in stages_data:
                cursor.execute('INSERT INTO stages (name, description, x, y) VALUES (?, ?, ?, ?)', (name, desc, x, y))

            # Enhanced tool data structure based on WG findings
            tool_data = {
                'CONCEPTUALISE': [
                    {
                        'category': 'Mind mapping, concept mapping and knowledge modelling',
                        'description': 'Tools that define the entities of research and their relationships',
                        'tools': [
                            {
                                'name': 'Miro',
                                'url': 'https://miro.com',
                                'provider': 'Miro',
                                'description': 'Real-time collaboration, virtual whiteboard, and templates for various purposes.',
                                'source_type': 'closed',
                                'scope': 'generic',
                                'interoperable': True,
                                'api_available': True,
                                'data_formats': ['PNG', 'PDF', 'JPG', 'CSV'],
                                'standards_compliant': []
                            },
                            {
                                'name': 'MindMeister',
                                'url': 'https://www.mindmeister.com/',
                                'provider': 'MeisterLabs',
                                'description': 'Collaborative, web-based mind mapping with integrations.',
                                'source_type': 'freemium',
                                'scope': 'generic',
                                'interoperable': True,
                                'api_available': True,
                                'data_formats': ['PDF', 'PNG', 'DOCX', 'PPTX'],
                                'standards_compliant': []
                            },
                            {
                                'name': 'XMind',
                                'url': 'https://www.xmind.net/',
                                'provider': 'XMind Ltd.',
                                'description': 'Full-featured mind mapping and brainstorming tool.',
                                'source_type': 'freemium',
                                'scope': 'generic',
                                'interoperable': True,
                                'api_available': False,
                                'data_formats': ['PDF', 'PNG', 'SVG', 'XLSX'],
                                'standards_compliant': []
                            }
                        ]
                    },
                    {
                        'category': 'Diagramming and flowchart',
                        'description': 'Tools that detail the research workflow',
                        'tools': [
                            {
                                'name': 'Lucidchart',
                                'url': 'https://www.lucidchart.com/',
                                'provider': 'Lucid Software',
                                'description': 'Collaborative diagramming with cloud integration.',
                                'source_type': 'closed',
                                'scope': 'generic',
                                'interoperable': True,
                                'api_available': True,
                                'data_formats': ['PDF', 'PNG', 'SVG', 'VSDX'],
                                'standards_compliant': ['BPMN 2.0']
                            },
                            {
                                'name': 'Draw.io (Diagrams.net)',
                                'url': 'https://app.diagrams.net/',
                                'provider': 'JGraph Ltd',
                                'description': 'Free online diagram software.',
                                'source_type': 'open',
                                'scope': 'generic',
                                'interoperable': True,
                                'api_available': False,
                                'data_formats': ['XML', 'PNG', 'SVG', 'PDF'],
                                'standards_compliant': ['BPMN 2.0', 'UML']
                            },
                            {
                                'name': 'Creately',
                                'url': 'https://creately.com/',
                                'provider': 'Cinergix Pty Ltd',
                                'description': 'Visual collaboration platform with templates.',
                                'source_type': 'freemium',
                                'scope': 'generic',
                                'interoperable': True,
                                'api_available': True,
                                'data_formats': ['PNG', 'PDF', 'SVG'],
                                'standards_compliant': []
                            }
                        ]
                    }
                ],
                'PLAN': [
                    {
                        'category': 'Data management planning (DMP)',
                        'description': 'Tools focused on enabling preparation and submission of data management plans',
                        'tools': [
                            {
                                'name': 'DMPTool',
                                'url': 'https://dmptool.org/',
                                'provider': 'California Digital Library',
                                'description': 'Free tool for creating data management plans.',
                                'source_type': 'open',
                                'scope': 'generic',
                                'interoperable': True,
                                'api_available': True,
                                'data_formats': ['PDF', 'DOCX', 'JSON'],
                                'standards_compliant': ['maDMP']
                            },
                            {
                                'name': 'DMPonline',
                                'url': 'https://dmponline.dcc.ac.uk/',
                                'provider': 'Digital Curation Centre',
                                'description': 'Tool for writing and sharing data management plans.',
                                'source_type': 'open',
                                'scope': 'generic',
                                'interoperable': True,
                                'api_available': True,
                                'data_formats': ['PDF', 'DOCX', 'JSON'],
                                'standards_compliant': ['maDMP']
                            },
                            {
                                'name': 'RDMO',
                                'url': 'https://rdmorganiser.github.io/',
                                'provider': 'RDMO Consortium',
                                'description': 'Research data management organiser.',
                                'source_type': 'open',
                                'scope': 'generic',
                                'interoperable': True,
                                'api_available': True,
                                'data_formats': ['XML', 'PDF', 'JSON'],
                                'standards_compliant': ['maDMP']
                            }
                        ]
                    }
                ]
            }

            # Get stage IDs
            cursor.execute('SELECT id, name FROM stages')
            stage_map = {name: id for id, name in cursor.fetchall()}

            # Insert tool categories and tools with enhanced metadata
            for stage_name, categories in tool_data.items():
                if stage_name in stage_map:
                    stage_id = stage_map[stage_name]
                    for category_data in categories:
                        cursor.execute('INSERT INTO tool_categories (stage_id, category, description) VALUES (?, ?, ?)', 
                                       (stage_id, category_data['category'], category_data['description']))
                        category_id = cursor.lastrowid
                        
                        for tool in category_data['tools']:
                            # Insert tool
                            cursor.execute('''INSERT INTO tools (category_id, name, url, provider, description) 
                                            VALUES (?, ?, ?, ?, ?)''', 
                                           (category_id, tool['name'], tool['url'], tool['provider'], tool['description']))
                            tool_id = cursor.lastrowid
                            
                            # Insert tool metadata
                            cursor.execute('''INSERT INTO tool_metadata 
                                            (tool_id, source_type, scope, interoperable, api_available, data_formats, standards_compliant) 
                                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                           (tool_id, tool['source_type'], tool['scope'], 
                                            tool['interoperable'], tool['api_available'],
                                            json.dumps(tool['data_formats']), json.dumps(tool['standards_compliant'])))

            # Insert connections
            connections_data = [
                ('circular', 'CONCEPTUALISE', 'PLAN', 'solid'),
                ('circular', 'PLAN', 'FUND', 'solid'),
                ('circular', 'FUND', 'COLLECT', 'solid'),
                ('circular', 'COLLECT', 'PROCESS', 'solid'),
                ('circular', 'PROCESS', 'ANALYSE', 'solid'),
                ('circular', 'ANALYSE', 'STORE', 'solid'),
                ('circular', 'STORE', 'PUBLISH', 'solid'),
                ('circular', 'PUBLISH', 'PRESERVE', 'solid'),
                ('circular', 'PRESERVE', 'SHARE', 'solid'),
                ('circular', 'SHARE', 'ACCESS', 'solid'),
                ('circular', 'ACCESS', 'TRANSFORM', 'solid'),
                ('circular', 'TRANSFORM', 'CONCEPTUALISE', 'solid'),
                ('circular', 'COLLECT', 'PROCESS', 'dashed'),
                ('circular', 'PROCESS', 'ANALYSE', 'dashed'),
                ('circular', 'ANALYSE', 'STORE', 'dashed')
            ]

            for view_mode, from_stage, to_stage, conn_type in connections_data:
                cursor.execute('INSERT INTO connections (view_mode, from_stage, to_stage, type) VALUES (?, ?, ?, ?)', 
                               (view_mode, from_stage, to_stage, conn_type))

            db.commit()
        logger.info("Database populated successfully with enhanced MaLDReTH data.")
    except Exception as e:
        logger.error(f"Error populating database: {e}")
        raise

# API Routes

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/curator')
def curator():
    """Render the curator interface."""
    return render_template('curator.html')

@app.route('/api/stages', methods=['GET'])
def get_stages():
    """Get all stages with their details."""
    try:
        stages = query_db('SELECT * FROM stages ORDER BY id')
        return jsonify([dict(stage) for stage in stages])
    except Exception as e:
        logger.error(f"Error getting stages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stage/<int:stage_id>', methods=['GET'])
def get_stage(stage_id):
    """Get a specific stage with its categories and tools."""
    try:
        stage = query_db('SELECT * FROM stages WHERE id = ?', [stage_id], one=True)
        if not stage:
            return jsonify({'error': 'Stage not found'}), 404
        
        categories = query_db('''
            SELECT tc.*, COUNT(t.id) as tool_count 
            FROM tool_categories tc 
            LEFT JOIN tools t ON tc.id = t.category_id 
            WHERE tc.stage_id = ? 
            GROUP BY tc.id
        ''', [stage_id])
        
        result = dict(stage)
        result['categories'] = [dict(cat) for cat in categories]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting stage: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools', methods=['GET'])
def get_all_tools():
    """Get all tools with their metadata."""
    try:
        tools = query_db('''
            SELECT t.*, tc.category, s.name as stage_name, tm.source_type, tm.scope, 
                   tm.interoperable, tm.api_available, tm.data_formats, tm.standards_compliant
            FROM tools t
            JOIN tool_categories tc ON t.category_id = tc.id
            JOIN stages s ON tc.stage_id = s.id
            LEFT JOIN tool_metadata tm ON t.id = tm.tool_id
            ORDER BY s.id, tc.id, t.name
        ''')
        
        result = []
        for tool in tools:
            tool_dict = dict(tool)
            # Parse JSON fields
            if tool_dict['data_formats']:
                tool_dict['data_formats'] = json.loads(tool_dict['data_formats'])
            if tool_dict['standards_compliant']:
                tool_dict['standards_compliant'] = json.loads(tool_dict['standards_compliant'])
            result.append(tool_dict)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tool/<int:tool_id>', methods=['GET', 'PUT'])
def manage_tool(tool_id):
    """Get or update a specific tool."""
    if request.method == 'GET':
        try:
            tool = query_db('''
                SELECT t.*, tm.source_type, tm.scope, tm.interoperable, 
                       tm.api_available, tm.data_formats, tm.standards_compliant
                FROM tools t
                LEFT JOIN tool_metadata tm ON t.id = tm.tool_id
                WHERE t.id = ?
            ''', [tool_id], one=True)
            
            if not tool:
                return jsonify({'error': 'Tool not found'}), 404
            
            tool_dict = dict(tool)
            if tool_dict['data_formats']:
                tool_dict['data_formats'] = json.loads(tool_dict['data_formats'])
            if tool_dict['standards_compliant']:
                tool_dict['standards_compliant'] = json.loads(tool_dict['standards_compliant'])
            
            return jsonify(tool_dict)
        except Exception as e:
            logger.error(f"Error getting tool: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            data = request.json
            with closing(get_db_connection()) as db:
                cursor = db.cursor()
                
                # Log the change
                old_tool = query_db('SELECT * FROM tools WHERE id = ?', [tool_id], one=True)
                if old_tool:
                    cursor.execute('''
                        INSERT INTO curation_log (entity_type, entity_id, action, old_value, new_value, curator_name, curator_email, reason)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', ('tool', tool_id, 'update', json.dumps(dict(old_tool)), json.dumps(data), 
                          data.get('curator_name'), data.get('curator_email'), data.get('reason')))
                
                # Update tool
                cursor.execute('''
                    UPDATE tools SET name = ?, url = ?, provider = ?, description = ?
                    WHERE id = ?
                ''', (data['name'], data['url'], data['provider'], data['description'], tool_id))
                
                # Update or insert metadata
                cursor.execute('SELECT id FROM tool_metadata WHERE tool_id = ?', [tool_id])
                if cursor.fetchone():
                    cursor.execute('''
                        UPDATE tool_metadata SET source_type = ?, scope = ?, interoperable = ?, 
                        api_available = ?, data_formats = ?, standards_compliant = ?
                        WHERE tool_id = ?
                    ''', (data.get('source_type'), data.get('scope'), data.get('interoperable', False),
                          data.get('api_available', False), json.dumps(data.get('data_formats', [])),
                          json.dumps(data.get('standards_compliant', [])), tool_id))
                else:
                    cursor.execute('''
                        INSERT INTO tool_metadata (tool_id, source_type, scope, interoperable, 
                        api_available, data_formats, standards_compliant)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (tool_id, data.get('source_type'), data.get('scope'), 
                          data.get('interoperable', False), data.get('api_available', False),
                          json.dumps(data.get('data_formats', [])), 
                          json.dumps(data.get('standards_compliant', []))))
                
                db.commit()
            
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.error(f"Error updating tool: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/interactions', methods=['GET', 'POST'])
def manage_interactions():
    """Get all interactions or create a new one."""
    if request.method == 'GET':
        try:
            interactions = query_db('''
                SELECT i.*, t1.name as from_tool_name, t2.name as to_tool_name
                FROM infrastructure_interactions i
                JOIN tools t1 ON i.from_tool_id = t1.id
                JOIN tools t2 ON i.to_tool_id = t2.id
                ORDER BY i.created_at DESC
            ''')
            return jsonify([dict(i) for i in interactions])
        except Exception as e:
            logger.error(f"Error getting interactions: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            interaction_id = insert_db('''
                INSERT INTO infrastructure_interactions 
                (from_tool_id, to_tool_id, interaction_type, interaction_description, 
                 data_flow_direction, integration_method, authentication_required)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data['from_tool_id'], data['to_tool_id'], data['interaction_type'],
                  data.get('interaction_description'), data.get('data_flow_direction', 'unidirectional'),
                  data.get('integration_method'), data.get('authentication_required', False)))
            
            # Log the creation
            insert_db('''
                INSERT INTO curation_log (entity_type, entity_id, action, new_value, curator_name, curator_email, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('interaction', interaction_id, 'create', json.dumps(data),
                  data.get('curator_name'), data.get('curator_email'), data.get('reason')))
            
            return jsonify({'status': 'success', 'id': interaction_id})
        except Exception as e:
            logger.error(f"Error creating interaction: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/interaction/<int:interaction_id>', methods=['PUT', 'DELETE'])
def manage_interaction(interaction_id):
    """Update or delete a specific interaction."""
    if request.method == 'PUT':
        try:
            data = request.json
            with closing(get_db_connection()) as db:
                cursor = db.cursor()
                
                # Verify interaction
                if data.get('verified'):
                    cursor.execute('''
                        UPDATE infrastructure_interactions 
                        SET verified = ?, verified_by = ?, verified_date = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (True, data.get('verified_by'), interaction_id))
                else:
                    cursor.execute('''
                        UPDATE infrastructure_interactions 
                        SET interaction_type = ?, interaction_description = ?, 
                            data_flow_direction = ?, integration_method = ?, 
                            authentication_required = ?
                        WHERE id = ?
                    ''', (data['interaction_type'], data.get('interaction_description'),
                          data.get('data_flow_direction'), data.get('integration_method'),
                          data.get('authentication_required', False), interaction_id))
                
                db.commit()
            
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.error(f"Error updating interaction: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            insert_db('DELETE FROM infrastructure_interactions WHERE id = ?', [interaction_id])
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.error(f"Error deleting interaction: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/curation-log', methods=['GET'])
def get_curation_log():
    """Get the curation log with optional filtering."""
    try:
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id')
        
        query = 'SELECT * FROM curation_log'
        params = []
        conditions = []
        
        if entity_type:
            conditions.append('entity_type = ?')
            params.append(entity_type)
        
        if entity_id:
            conditions.append('entity_id = ?')
            params.append(entity_id)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC LIMIT 100'
        
        logs = query_db(query, params)
        return jsonify([dict(log) for log in logs])
    except Exception as e:
        logger.error(f"Error getting curation log: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/tools', methods=['GET'])
def search_tools():
    """Search tools by name, provider, or characteristics."""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify([])
        
        search_pattern = f'%{search_term}%'
        tools = query_db('''
            SELECT DISTINCT t.*, tc.category, s.name as stage_name
            FROM tools t
            JOIN tool_categories tc ON t.category_id = tc.id
            JOIN stages s ON tc.stage_id = s.id
            LEFT JOIN tool_metadata tm ON t.id = tm.tool_id
            WHERE t.name LIKE ? OR t.provider LIKE ? OR t.description LIKE ?
               OR tc.category LIKE ? OR s.name LIKE ?
            ORDER BY t.name
        ''', [search_pattern] * 5)
        
        return jsonify([dict(tool) for tool in tools])
    except Exception as e:
        logger.error(f"Error searching tools: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/interactions', methods=['GET'])
def export_interactions():
    """Export infrastructure interactions as JSON."""
    try:
        interactions = query_db('''
            SELECT i.*, t1.name as from_tool_name, t2.name as to_tool_name,
                   tc1.category as from_category, tc2.category as to_category,
                   s1.name as from_stage, s2.name as to_stage
            FROM infrastructure_interactions i
            JOIN tools t1 ON i.from_tool_id = t1.id
            JOIN tools t2 ON i.to_tool_id = t2.id
            JOIN tool_categories tc1 ON t1.category_id = tc1.id
            JOIN tool_categories tc2 ON t2.category_id = tc2.id
            JOIN stages s1 ON tc1.stage_id = s1.id
            JOIN stages s2 ON tc2.stage_id = s2.id
            ORDER BY s1.id, s2.id
        ''')
        
        result = {
            'export_date': datetime.now().isoformat(),
            'total_interactions': len(interactions),
            'interactions': [dict(i) for i in interactions]
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error exporting interactions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get statistics about the infrastructure data."""
    try:
        stats = {}
        
        # Basic counts
        stats['total_stages'] = query_db('SELECT COUNT(*) FROM stages', one=True)[0]
        stats['total_categories'] = query_db('SELECT COUNT(*) FROM tool_categories', one=True)[0]
        stats['total_tools'] = query_db('SELECT COUNT(*) FROM tools', one=True)[0]
        stats['total_interactions'] = query_db('SELECT COUNT(*) FROM infrastructure_interactions', one=True)[0]
        stats['verified_interactions'] = query_db('SELECT COUNT(*) FROM infrastructure_interactions WHERE verified = 1', one=True)[0]
        
        # Tools by source type
        source_types = query_db('''
            SELECT source_type, COUNT(*) as count 
            FROM tool_metadata 
            WHERE source_type IS NOT NULL 
            GROUP BY source_type
        ''')
        stats['tools_by_source_type'] = {row['source_type']: row['count'] for row in source_types}
        
        # Tools by scope
        scopes = query_db('''
            SELECT scope, COUNT(*) as count 
            FROM tool_metadata 
            WHERE scope IS NOT NULL 
            GROUP BY scope
        ''')
        stats['tools_by_scope'] = {row['scope']: row['count'] for row in scopes}
        
        # Interoperable tools
        stats['interoperable_tools'] = query_db('SELECT COUNT(*) FROM tool_metadata WHERE interoperable = 1', one=True)[0]
        stats['api_available_tools'] = query_db('SELECT COUNT(*) FROM tool_metadata WHERE api_available = 1', one=True)[0]
        
        # Most connected tools
        most_connected = query_db('''
            SELECT t.name, COUNT(DISTINCT i.id) as connection_count
            FROM tools t
            LEFT JOIN infrastructure_interactions i ON t.id = i.from_tool_id OR t.id = i.to_tool_id
            GROUP BY t.id
            HAVING connection_count > 0
            ORDER BY connection_count DESC
            LIMIT 10
        ''')
        stats['most_connected_tools'] = [dict(row) for row in most_connected]
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/initialize', methods=['POST'])
def initialize_database():
    """Initialize and populate the database."""
    try:
        init_db()
        populate_db()
        return jsonify({'status': 'success', 'message': 'Database initialized and populated successfully'})
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return jsonify({'error': 'Failed to initialize database: ' + str(e)}), 500

# Initialize database on startup
def initialize_app():
    """Initialize the application and database."""
    try:
        init_db()
        # Check if database is empty and populate if needed
        stages = query_db('SELECT COUNT(*) FROM stages')
        if stages and stages[0][0] == 0:
            logger.info("Database is empty, populating with initial data...")
            populate_db()
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        # Don't raise here to allow the app to start even if initialization fails

# Initialize the app when module is imported
try:
    initialize_app()
except Exception as e:
    logger.error(f"Failed to initialize app on import: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', APP_CONFIG['PORT']))
    app.run(host=APP_CONFIG['HOST'], port=port, debug=APP_CONFIG['DEBUG'])
