# MaLDReTH Project Cleanup Summary

## Files to Delete

### 1. Backup/Temporary Files
- `app.py.backup`
- `app.py.backup.20250620_145700`
- `hotfix.sh`
- `models_phase2.py`

### 2. Redundant Scripts (functionality moved to main scripts)
- `fix_heroku_db.py`
- `fix_tool_categories_schema.py`
- `fix_tool_categories.py`
- `reset_heroku_db.py`
- `heroku_init.py`
- `init_heroku_db.py`
- `import_tools_only.py`
- `migrate_maldreth_data.py` (use migrate_maldreth_data_standalone.py)
- `inspect_database.py`

### 3. Empty/Unused Files
- `google_integration.py` (empty)
- `sample_data.json` (empty)
- `config.py` (empty - replaced with proper version)
- Empty scripts in `scripts/` directory

### 4. Local Development Files
- `interactions.db` (local SQLite database)
- `instance/` directory (Flask instance folder)

## Files Created/Updated

### 1. Project Configuration
- ✅ `setup.py` - Package setup configuration
- ✅ `pytest.ini` - Pytest configuration
- ✅ `MANIFEST.in` - Package manifest
- ✅ `config.py` - Proper configuration module

### 2. Utilities Module
- ✅ `utils/__init__.py` - Utilities package init
- ✅ `utils/helpers.py` - Helper functions

### 3. Documentation
- ✅ `CONTRIBUTING.md` - Contribution guidelines
- ✅ `cleanup_project.sh` - Cleanup script

### 4. Directory Structure
Need to create:
- `static/` - Static assets directory
  - `static/css/` - Stylesheets
  - `static/js/` - JavaScript files  
  - `static/images/` - Images
- `data/` - Data files directory
  - `data/csv/` - CSV data files

## Actions to Take

1. **Run the cleanup script**:
   ```bash
   chmod +x cleanup_project.sh
   ./cleanup_project.sh
   ```

2. **Create missing files**:
   ```bash
   # Create static files
   touch static/css/style.css
   touch static/js/main.js
   
   # Create additional documentation
   echo "# Changelog\n\nAll notable changes to this project will be documented in this file." > CHANGELOG.md
   echo "# Code of Conduct\n\nPlease be respectful and inclusive." > CODE_OF_CONDUCT.md
   ```

3. **Move scripts to proper location**:
   ```bash
   mv init_maldreth_tools.py scripts/
   mv migrate_maldreth_data_standalone.py scripts/
   ```

4. **Update imports** in moved scripts:
   - Change `from app import` to `from ..app import`
   - Or run scripts from project root

5. **Commit changes**:
   ```bash
   git add -A
   git commit -m "chore: Clean up project structure and remove redundant files"
   ```

## Files to Keep

### Core Application Files
- ✅ `app.py` - Main Flask application
- ✅ `models.py` - Database models
- ✅ `routes.py` - API routes
- ✅ `api_v2.py` - Version 2 API (if still needed)

### Scripts (move to scripts/)
- ✅ `init_maldreth_tools.py` - Initialize database from Excel/CSV
- ✅ `migrate_maldreth_data_standalone.py` - Migrate data from CSV
- ✅ `create_tables.py` - Create database tables
- ✅ `init_db.py` - Initialize database
- ✅ `deploy_to_heroku.py` - Deployment script

### Configuration Files
- ✅ `.env` - Environment variables (not in git)
- ✅ `.env.example` - Example environment variables
- ✅ `.gitignore` - Git ignore rules
- ✅ `requirements.txt` - Python dependencies
- ✅ `requirements-dev.txt` - Development dependencies
- ✅ `runtime.txt` - Python version for Heroku
- ✅ `Procfile` - Heroku process file
- ✅ `app.json` - Heroku app configuration
- ✅ `docker-compose.yml` - Docker compose config
- ✅ `Dockerfile` - Docker configuration

### Documentation
- ✅ `README.md` - Project documentation
- ✅ `LICENSE` - Apache 2.0 license
- ✅ Other .md files for documentation

### Tests
- ✅ `tests/` directory with test files

### Templates
- ✅ `templates/` directory with HTML templates

### CI/CD
- ✅ `.github/workflows/ci.yml` - GitHub Actions workflow

## Project Structure After Cleanup

```
maldreth-infrastructure/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── api_v2.py
├── data/
│   ├── csv/
│   └── research_data_lifecycle.xlsx
├── scripts/
│   ├── __init__.py
│   ├── init_maldreth_tools.py
│   ├── migrate_maldreth_data_standalone.py
│   ├── create_tables.py
│   ├── init_db.py
│   └── deploy_to_heroku.py
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── .gitkeep
├── templates/
│   ├── base.html
│   ├── index.html
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── test_app.py
│   └── test_models.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── .env
├── .env.example
├── .gitignore
├── app.py
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── config.py
├── CONTRIBUTING.md
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── MANIFEST.in
├── Procfile
├── pytest.ini
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── runtime.txt
├── setup.py
└── updates.txt
```

## Benefits of Cleanup

1. **Cleaner Structure**: Organized files into logical directories
2. **No Redundancy**: Removed duplicate and backup files
3. **Better Maintainability**: Clear separation of concerns
4. **Professional Setup**: Proper Python package structure
5. **CI/CD Ready**: All necessary configuration files in place
6. **Documentation**: Comprehensive docs for contributors

## Next Steps

After cleanup:
1. Test the application to ensure nothing broke
2. Update any import statements if needed
3. Run the test suite
4. Deploy to staging environment
5. Update documentation if needed
