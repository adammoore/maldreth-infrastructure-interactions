#!/usr/bin/env python3
"""
Rebuild CI/CD initialization to prevent duplicate tools
"""
import sys
sys.path.append('.')

def create_robust_init_process():
    """Create a robust initialization process that prevents duplicates."""
    
    # 1. Update the database initialization function in streamlined_app.py
    init_function_replacement = '''def init_database_with_maldreth_data():
    """Initialize database with MaLDReTH 1.0 data, preventing duplicates."""
    logger.info("Starting database initialization with duplicate prevention...")
    
    # Check if data already exists (skip if already populated)
    existing_stages = MaldrethStage.query.count()
    existing_tools = ExemplarTool.query.filter_by(is_active=True).count()
    
    if existing_stages >= 12 and existing_tools > 50:
        logger.info(f"Database already populated: {existing_stages} stages, {existing_tools} tools - skipping initialization")
        return
    
    logger.info("Database needs initialization - proceeding with data setup...")
    
    # Deactivate any existing auto-created tools to prevent conflicts
    auto_tools = ExemplarTool.query.filter_by(auto_created=True, is_active=True).all()
    for tool in auto_tools:
        tool.is_active = False
    logger.info(f"Deactivated {len(auto_tools)} existing auto-created tools")
    
    # MaLDReTH 1.0 reference data (simplified for reliability)
    maldreth_data = {
        "CONCEPTUALISE": {
            "description": "To formulate the initial research idea or hypothesis, and define the scope of the research project and data requirements.",
            "categories": {
                "Mind mapping, concept mapping and knowledge modelling": ["FreeMind", "XMind", "Lucidchart", "Miro", "Roam Research"],
                "Diagramming and flowchart": ["Draw.io", "Visio", "Creately"],
                "Literature review": ["Zotero", "Mendeley"]
            }
        },
        "PLAN": {
            "description": "To establish a structured strategic framework for management of the research project, outlining aims, objectives, methodologies, and resource allocation.",
            "categories": {
                "Data management planning (DMP)": ["DMPTool", "DMP Assistant", "DMPT"],
                "Project planning": ["Gantt Project", "Microsoft Project", "Trello"],
                "Research methodology": ["NVivo", "Atlas.ti"]
            }
        },
        "FUND": {
            "description": "To identify and acquire financial resources to support the research project, including data collection, analysis, storage, and dissemination activities.",
            "categories": {}  # No specific tools for funding stage
        },
        "COLLECT": {
            "description": "To gather primary and secondary data according to the research methodology and ethical guidelines established during the planning phase.",
            "categories": {
                "Survey and questionnaire": ["SurveyMonkey", "Google Forms", "Qualtrics"],
                "Data collection": ["ODK", "KoBoToolbox", "REDCap"],
                "Field data collection": ["Epicollect5", "Survey123", "Fulcrum"]
            }
        },
        "PROCESS": {
            "description": "To transform, clean, validate, and prepare raw data for analysis, ensuring data quality and consistency.",
            "categories": {
                "Electronic Laboratory Notebooks (ELNs)": ["LabArchives", "eLabJournal"],
                "Scientific computing across all programming languages": ["Jupyter", "RStudio"],
                "Data cleaning and transformation": ["OpenRefine", "Trifacta", "DataLadder"]
            }
        },
        "ANALYSE": {
            "description": "To examine, interpret, and derive insights from processed data using appropriate analytical methods and tools.",
            "categories": {
                "Statistical analysis": ["R", "SPSS", "SAS"],
                "Data visualization": ["Tableau", "D3.js"],
                "Machine learning": ["Python scikit-learn", "TensorFlow"]
            }
        },
        "STORE": {
            "description": "To securely store processed data and analysis results in appropriate formats and locations for future access and use.",
            "categories": {
                "Data repository": ["Figshare", "Zenodo"],
                "Archive": ["DSpace"],
                "Cloud storage": ["Google Drive", "Dropbox", "OneDrive"]
            }
        },
        "PUBLISH": {
            "description": "To share research findings and datasets through appropriate channels, ensuring proper attribution and accessibility.",
            "categories": {
                "Academic publishing": ["LaTeX", "Overleaf", "Word"],
                "Data publication": ["Dataverse", "Figshare"],
                "Preprint servers": ["arXiv", "bioRxiv", "PeerJ Preprints"]
            }
        },
        "PRESERVE": {
            "description": "To ensure long-term accessibility and integrity of research data and outputs through appropriate preservation strategies.",
            "categories": {
                "Digital preservation": ["LOCKSS", "Fedora", "DSpace", "Samvera"],
                "Data repository": ["Institutional Repository", "Domain Repository", "Zenodo", "Figshare"],
                "Archive": ["Digital preservation system"]
            }
        },
        "SHARE": {
            "description": "To make research data and findings available to other researchers and stakeholders through appropriate sharing mechanisms.",
            "categories": {
                "Data repository": ["GitHub", "Zenodo"],
                "Electronic Laboratory Notebooks (ELNs)": ["LabArchives", "Benchling", "eLabNext", "Lab Archives"],
                "Scientific computing across all programming languages": ["Jupyter", "Eclipse", "Jupyter"]
            }
        },
        "ACCESS": {
            "description": "To provide controlled and documented access to research data for verification, reuse, and further research activities.",
            "categories": {
                "Data repository": ["DataCite", "CKAN"],
                "Access control": ["Shibboleth", "OAuth"],
                "Data discovery": ["DataCite", "Google Dataset Search", "CKAN"]
            }
        },
        "TRANSFORM": {
            "description": "To convert and adapt research data and outputs into new formats, applications, or research contexts.",
            "categories": {
                "Data transformation": ["Apache Spark", "Talend", "Pentaho"],
                "Electronic Laboratory Notebooks (ELNs)": ["LabArchives"],
                "Format conversion": ["Pandoc", "ImageMagick", "FFmpeg"]
            }
        }
    }
    
    # Create or update stages and categories
    for position, (stage_name, stage_info) in enumerate(maldreth_data.items()):
        # Get or create stage
        stage = MaldrethStage.query.filter_by(name=stage_name).first()
        if not stage:
            stage = MaldrethStage(
                name=stage_name,
                description=stage_info["description"],
                position=position
            )
            db.session.add(stage)
            db.session.flush()  # Get the stage ID
        
        # Create categories and tools for this stage
        for category_name, tools in stage_info["categories"].items():
            # Get or create category
            category = ToolCategory.query.filter_by(
                name=category_name, 
                stage_id=stage.id
            ).first()
            
            if not category:
                category = ToolCategory(
                    name=category_name,
                    stage_id=stage.id,
                    description=f"Category for {category_name} tools in {stage_name} stage"
                )
                db.session.add(category)
                db.session.flush()  # Get the category ID
            
            # Add tools to this category (prevent duplicates)
            for tool_name in tools:
                # Check if tool already exists in this category
                existing_tool = ExemplarTool.query.filter_by(
                    name=tool_name,
                    category_id=category.id,
                    stage_id=stage.id,
                    is_active=True
                ).first()
                
                if not existing_tool:
                    tool = ExemplarTool(
                        name=tool_name,
                        stage_id=stage.id,
                        category_id=category.id,
                        description=f"{tool_name} - {category_name} tool for {stage_name}",
                        is_active=True,
                        auto_created=True,
                        import_source="MaLDReTH 1.0 Initial Data"
                    )
                    db.session.add(tool)
    
    # Commit all changes
    db.session.commit()
    
    # Final statistics
    total_stages = MaldrethStage.query.count()
    total_categories = ToolCategory.query.count()
    total_active_tools = ExemplarTool.query.filter_by(is_active=True).count()
    
    logger.info(f"Database initialization complete:")
    logger.info(f"  Stages: {total_stages}")
    logger.info(f"  Categories: {total_categories}")  
    logger.info(f"  Active tools: {total_active_tools}")'''
    
    # Read the current streamlined_app.py
    with open('/Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/streamlined_app.py', 'r') as f:
        content = f.read()
    
    # Find and replace the init function
    start_marker = 'def init_database_with_maldreth_data():'
    end_marker = '    logger.info("Database initialized with MaLDReTH 1.0 data.")'
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker) + len(end_marker)
    
    if start_pos != -1 and end_pos != -1:
        new_content = content[:start_pos] + init_function_replacement + content[end_pos:]
        
        with open('/Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/streamlined_app.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Updated init_database_with_maldreth_data() function")
        return True
    else:
        print("❌ Could not find init function to replace")
        return False

def create_heroku_release_command():
    """Create/update Heroku release command for clean deployments."""
    
    release_script_content = '''#!/usr/bin/env python3
"""
Heroku release command - runs before each deployment
Ensures clean database state and prevents duplicates
"""
import sys
import os
sys.path.append('.')

# Set environment for Heroku
os.environ.setdefault('FLASK_APP', 'wsgi.py')

from streamlined_app import app, db, logger, ExemplarTool
from clean_update import clean_update

def heroku_release():
    """Run clean update process for Heroku releases."""
    logger.info("=== HEROKU RELEASE PROCESS ===")
    
    with app.app_context():
        try:
            # Run clean update to prevent duplicates
            success = clean_update()
            
            if success:
                logger.info("✅ Heroku release process completed successfully")
                return True
            else:
                logger.error("❌ Heroku release process failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Heroku release error: {e}")
            return False

if __name__ == "__main__":
    success = heroku_release()
    sys.exit(0 if success else 1)'''
    
    with open('/Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/heroku_release.py', 'w') as f:
        f.write(release_script_content)
    
    # Update Procfile to use the release command
    procfile_content = '''release: python heroku_release.py
web: gunicorn wsgi:app'''
    
    with open('/Users/adamvialsmoore/Workspace/maldreth-infrastructure-interactions/Procfile', 'w') as f:
        f.write(procfile_content)
    
    print("✅ Created heroku_release.py script")
    print("✅ Updated Procfile with release command")

def main():
    print("Rebuilding CI/CD Initialization")
    print("=" * 40)
    
    # Update the initialization function
    if create_robust_init_process():
        print("\n✅ Database initialization function updated")
    else:
        print("\n❌ Failed to update initialization function")
        return
    
    # Create Heroku release process
    create_heroku_release_command()
    
    print("\n📋 Changes Made:")
    print("1. ✅ Updated init_database_with_maldreth_data() with duplicate prevention")
    print("2. ✅ Created heroku_release.py for clean deployments")
    print("3. ✅ Updated Procfile with release command")
    
    print("\n🚀 Next Steps:")
    print("1. Test locally: python3 streamlined_app.py")
    print("2. Commit changes: git add . && git commit -m 'Rebuild CI/CD initialization'")
    print("3. Deploy: git push heroku main")
    print("4. Monitor release logs: heroku logs --tail")

if __name__ == "__main__":
    main()