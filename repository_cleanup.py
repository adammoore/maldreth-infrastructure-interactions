#!/usr/bin/env python3
"""
Repository Cleanup Utility for PRISM
Identifies and moves/removes unnecessary files to streamline the repository
"""

import os
import shutil
from pathlib import Path

# Define the root directory
ROOT_DIR = Path(__file__).parent

# Files to remove (debug, testing, temporary files)
FILES_TO_REMOVE = [
    'clean_update.py',
    'fix_duplicate_tools.py', 
    'debug_viz_data.py',
    'check_production_tools.py',
    'category_cleanup_and_update.py',
    'safe_category_cleanup.py',
    'debug_enhanced_viz.py',
    'investigate_data_issues.py',
    'debug_d3_issues.py',
    'tool_deduplication.py',
    'rebuild_cicd_init.py',
    'heroku_release.py'
]

# Documentation files to consolidate or remove
DOCS_TO_REMOVE = [
    'CLEANUP_SUMMARY.md',
    'DEPLOYMENT_CHECKLIST.md', 
    'DEPLOYMENT_GUIDE.md',
    'FILE_CONTENT_GUIDE.md',
    'GOOGLE_FORM_SETUP.md',
    'INTEGRATION_GUIDE.md',
    'QUICK_REFERENCE.md',
    'RELEASE_NOTES.md',
    'TOOL_MANAGEMENT_IMPROVEMENTS.md',
    'TROUBLESHOOTING.md'
]

# Files to keep as they're essential
ESSENTIAL_FILES = [
    'README.md',
    'CONTRIBUTING.md', 
    'LICENSE',
    'Procfile',
    'requirements.txt',
    'app.json',
    'wsgi.py',
    'streamlined_app.py',
    'database_management.py',
    'demo_interactions.csv'
]

def create_backup_directory():
    """Create a backup directory for removed files"""
    backup_dir = ROOT_DIR / 'archive_removed_files'
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def cleanup_files():
    """Remove unnecessary files and create cleaner repository structure"""
    print("🧹 PRISM Repository Cleanup")
    print("=" * 50)
    
    backup_dir = create_backup_directory()
    removed_count = 0
    
    print("Removing debug and temporary files...")
    for file_name in FILES_TO_REMOVE:
        file_path = ROOT_DIR / file_name
        if file_path.exists():
            shutil.move(str(file_path), str(backup_dir / file_name))
            print(f"  ✅ Moved {file_name} to archive")
            removed_count += 1
        else:
            print(f"  ⚠️  {file_name} not found")
    
    print("\nConsolidating documentation files...")
    for doc_name in DOCS_TO_REMOVE:
        doc_path = ROOT_DIR / doc_name
        if doc_path.exists():
            shutil.move(str(doc_path), str(backup_dir / doc_name))
            print(f"  ✅ Moved {doc_name} to archive")
            removed_count += 1
    
    # Clean up any __pycache__ directories
    print("\nCleaning Python cache files...")
    for pycache in ROOT_DIR.rglob('__pycache__'):
        if pycache.is_dir():
            shutil.rmtree(pycache)
            print(f"  ✅ Removed {pycache}")
    
    # Clean up any .pyc files
    for pyc_file in ROOT_DIR.rglob('*.pyc'):
        pyc_file.unlink()
        print(f"  ✅ Removed {pyc_file}")
    
    print(f"\n🎉 Cleanup complete! Moved {removed_count} files to archive.")
    print(f"Archive location: {backup_dir}")
    
    return backup_dir

def create_docs_directory():
    """Create organized docs directory"""
    docs_dir = ROOT_DIR / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    # Create essential documentation
    (docs_dir / 'API.md').write_text("""# PRISM API Documentation

## Overview
PRISM provides RESTful API endpoints for accessing tool and interaction data.

## Endpoints

### Tools
- `GET /api/v1/tools` - List all tools
- `GET /api/v1/tools/{id}` - Get specific tool

### Interactions  
- `GET /api/v1/interactions` - List all interactions
- `POST /api/interactions` - Submit new interaction

### Export/Import
- `GET /export/interactions/csv` - Export CSV
- `POST /upload/interactions/csv` - Import CSV

## Authentication
Most endpoints are public. Write operations may require authentication in future versions.
""")

    (docs_dir / 'DEPLOYMENT.md').write_text("""# PRISM Deployment Guide

## Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Git repository configured
- PostgreSQL add-on

### Steps
1. `heroku create your-app-name`
2. `heroku addons:create heroku-postgresql:mini`  
3. `git push heroku main`
4. `heroku run flask db upgrade`

## Local Development
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python streamlined_app.py`

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key
- `FLASK_ENV` - development or production
""")

    (docs_dir / 'CONTRIBUTING.md').write_text("""# Contributing to PRISM

## Ways to Contribute

### Data Contribution
- Add tool interactions via web interface
- Upload CSV data with tool mappings
- Improve tool descriptions and metadata

### Code Contribution
- Submit bug fixes and improvements
- Add new visualization features  
- Enhance API functionality

### Documentation
- Improve README and docs
- Add examples and tutorials
- Translate to other languages

## Development Process
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## Code Standards
- Follow PEP 8 for Python code
- Add docstrings to functions
- Include unit tests for new features
- Update documentation as needed
""")

    print(f"✅ Created organized docs directory: {docs_dir}")

def show_final_structure():
    """Show the cleaned repository structure"""
    print("\n📁 FINAL REPOSITORY STRUCTURE")
    print("=" * 50)
    
    # Show key directories and files
    important_paths = [
        'streamlined_app.py',
        'database_management.py', 
        'README.md',
        'CONTRIBUTING.md',
        'requirements.txt',
        'Procfile',
        'templates/',
        'static/',
        'data/',
        'docs/',
        'migrations/',
        'demo_interactions.csv'
    ]
    
    for path_str in important_paths:
        path = ROOT_DIR / path_str
        if path.exists():
            if path.is_dir():
                file_count = len(list(path.iterdir()))
                print(f"  📁 {path_str} ({file_count} files)")
            else:
                size_kb = path.stat().st_size // 1024
                print(f"  📄 {path_str} ({size_kb}KB)")
        else:
            print(f"  ❌ {path_str} (missing)")

def main():
    """Main cleanup process"""
    print("This will clean up the PRISM repository by removing debug files")
    print("and organizing documentation. Files will be moved to an archive folder.")
    print()
    
    confirm = input("Proceed with cleanup? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        backup_dir = cleanup_files()
        create_docs_directory()
        show_final_structure()
        
        print("\n🎯 NEXT STEPS:")
        print("1. Review the archive folder and delete if satisfied")
        print("2. Commit the cleaned repository structure") 
        print("3. Update any CI/CD references to removed files")
        print("4. Test the application to ensure nothing is broken")
        
    else:
        print("Cleanup cancelled")

if __name__ == '__main__':
    main()