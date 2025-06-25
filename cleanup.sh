#!/bin/bash
# cleanup_project.sh - Clean up redundant files and organize project structure

echo "MaLDReTH Project Cleanup Script"
echo "==============================="

# Create backup directory
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Created backup directory: $BACKUP_DIR"

# Backup files before deletion
echo -e "\nBacking up files..."

# Backup old files
files_to_backup=(
    "app.py.backup"
    "app.py.backup.20250620_145700"
    "hotfix.sh"
    "fix_heroku_db.py"
    "fix_tool_categories_schema.py"
    "fix_tool_categories.py"
    "reset_heroku_db.py"
    "heroku_init.py"
    "init_heroku_db.py"
    "import_tools_only.py"
    "migrate_maldreth_data.py"
    "interactions.db"
    "inspect_database.py"
)

for file in "${files_to_backup[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "  Backed up: $file"
    fi
done

# Delete redundant files
echo -e "\nRemoving redundant files..."

files_to_delete=(
    "app.py.backup"
    "app.py.backup.20250620_145700"
    "hotfix.sh"
    "fix_heroku_db.py"
    "fix_tool_categories_schema.py"
    "fix_tool_categories.py"
    "reset_heroku_db.py"
    "heroku_init.py"
    "init_heroku_db.py"
    "import_tools_only.py"
    "migrate_maldreth_data.py"
    "google_integration.py"
    "sample_data.json"
    "interactions.db"
    "inspect_database.py"
)

for file in "${files_to_delete[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  Removed: $file"
    fi
done

# Create missing directories
echo -e "\nCreating directory structure..."

directories=(
    "static"
    "static/css"
    "static/js"
    "static/images"
    "data"
    "data/csv"
    "utils"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  Created: $dir/"
    fi
done

# Create __init__.py files for Python packages
touch utils/__init__.py

# Move models_phase2.py to backup
if [ -f "models_phase2.py" ]; then
    mv "models_phase2.py" "$BACKUP_DIR/"
    echo -e "\nMoved models_phase2.py to backup"
fi

# Create .gitkeep files for empty directories
touch static/images/.gitkeep
touch data/csv/.gitkeep

echo -e "\nCleanup complete!"
echo "Backup stored in: $BACKUP_DIR"
echo -e "\nNext steps:"
echo "1. Review the backup directory to ensure no important files were removed"
echo "2. Run 'git add -A' to stage all changes"
echo "3. Commit the cleanup: git commit -m 'chore: Clean up project structure and remove redundant files'"
