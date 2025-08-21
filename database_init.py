#!/usr/bin/env python3
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
