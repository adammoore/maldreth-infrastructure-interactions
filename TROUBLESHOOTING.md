# Troubleshooting Guide

## Database Issues

### ERROR: relation "maldreth_stages" does not exist

**Symptoms**: Application crashes on startup with database relation errors

**Root Cause**: Schema mismatch between different model definitions in the codebase

**Problem**: The application has two different model systems:
- `models.py` - uses `Stage` model with `stages` table
- `streamlined_app.py` - uses `MaldrethStage` model with `maldreth_stages` table

**Resolution**:

1. **For Heroku Production**:
   ```bash
   # Reset the database completely
   heroku pg:reset DATABASE_URL --app your-app-name --confirm your-app-name
   
   # Reinitialize with correct schema
   heroku run --app your-app-name "python -c \"from streamlined_app import app, init_database_with_maldreth_data; app.app_context().push(); init_database_with_maldreth_data()\""
   ```

2. **For Local Development**:
   ```bash
   # Use the streamlined initialization script
   python init_streamlined_db.py
   ```

**Prevention**: Always ensure your WSGI entry point (`wsgi.py`) matches the model definitions you're using.

### Database Connection Issues

**Symptoms**: Connection timeouts or authentication failures

**Solutions**:
- Check `DATABASE_URL` environment variable
- Verify PostgreSQL add-on is active in Heroku
- Ensure database credentials are correct

## Heroku Deployment Issues

### Web Process Won't Start

**Check Process Status**:
```bash
heroku ps --app your-app-name
```

**View Logs**:
```bash
heroku logs --tail --app your-app-name
```

**Common Solutions**:
- Verify `Procfile` configuration
- Check Python version in `runtime.txt`
- Ensure all dependencies in `requirements.txt`

### Environment Variables

**List Current Config**:
```bash
heroku config --app your-app-name
```

**Set Required Variables**:
```bash
heroku config:set SECRET_KEY=your-secret-key --app your-app-name
```

## Data Management

### Adding New Tool Interactions

Use the provided scripts:
```bash
# Local development
python add_dmptool_entry.py

# Production (run via Heroku)
heroku run --app your-app-name python add_dmptool_entry.py
```

### Database Reinitialization

**⚠️ WARNING**: This will delete all existing data

```bash
# Complete reinitialization
python init_streamlined_db.py
```

## Application Errors

### Internal Server Error (500)

**Check logs for specific error messages**:
```bash
heroku logs --tail --app your-app-name
```

**Common causes**:
- Database connection issues
- Missing environment variables
- Schema mismatches
- Import errors

### Form Validation Errors

**Symptoms**: Forms not submitting or validation messages

**Solutions**:
- Check CSRF token configuration
- Verify form field validation rules
- Ensure proper error handling in templates

## Local Development Issues

### Virtual Environment Setup

```bash
# Create new environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Setup for Development

```bash
# Using SQLite for local development
export DATABASE_URL=sqlite:///local_development.db

# Initialize database
python init_streamlined_db.py
```

## Performance Issues

### Slow Database Queries

**Check query performance**:
- Enable query logging
- Use database query analyzers
- Review indexes on frequently queried columns

### Memory Usage

**Monitor Heroku metrics**:
```bash
heroku logs --ps web.1 --tail --app your-app-name
```

## Support Resources

### Log Analysis

**Get comprehensive logs**:
```bash
# Recent logs
heroku logs --num 1500 --app your-app-name

# Specific process logs
heroku logs --ps web.1 --app your-app-name
```

### Database Analysis

**Connect to production database**:
```bash
heroku pg:psql --app your-app-name
```

**Basic database queries**:
```sql
-- Check table structure
\dt

-- Count records in main tables
SELECT 'maldreth_stages' as table_name, COUNT(*) FROM maldreth_stages
UNION ALL
SELECT 'tool_categories', COUNT(*) FROM tool_categories
UNION ALL  
SELECT 'exemplar_tools', COUNT(*) FROM exemplar_tools
UNION ALL
SELECT 'tool_interactions', COUNT(*) FROM tool_interactions;
```

### Configuration Verification

**Verify critical configuration**:
```bash
# Check if all required variables are set
heroku config:get SECRET_KEY --app your-app-name
heroku config:get DATABASE_URL --app your-app-name
```

### Health Checks

**Basic health verification**:
```bash
# Test application endpoint
curl https://your-app-name.herokuapp.com/

# Check database connectivity
heroku run --app your-app-name "python -c \"from streamlined_app import app, db; app.app_context().push(); print('DB connection:', db.engine.execute('SELECT 1').scalar())\""
```

## Getting Help

### Before Reporting Issues

1. Check this troubleshooting guide
2. Review recent logs for error messages
3. Verify environment configuration
4. Test with minimal reproduction steps

### Reporting Issues

Include in your report:
- Exact error message
- Steps to reproduce
- Environment (local/Heroku)
- Recent changes made
- Relevant log excerpts

### Emergency Recovery

**If production is completely down**:

1. **Immediate triage**:
   ```bash
   heroku logs --tail --app your-app-name
   heroku ps --app your-app-name
   ```

2. **Database recovery**:
   ```bash
   # Check if database is accessible
   heroku pg:info --app your-app-name
   
   # Last resort: reset and reinitialize
   heroku pg:reset DATABASE_URL --app your-app-name --confirm your-app-name
   heroku run --app your-app-name "python -c \"from streamlined_app import app, init_database_with_maldreth_data; app.app_context().push(); init_database_with_maldreth_data()\""
   ```

3. **Verify recovery**:
   ```bash
   curl https://your-app-name.herokuapp.com/
   heroku logs --num 100 --app your-app-name
   ```
