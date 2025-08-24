# PRISM Deployment Guide

## Overview
PRISM is designed for flexible deployment across different environments, with production deployment on Heroku and local development support.

## Production Deployment (Heroku)

### Prerequisites
- Heroku CLI installed and configured
- Git repository with PRISM code
- Heroku account with appropriate permissions

### Step-by-Step Deployment

#### 1. Create Heroku Application
```bash
# Create new Heroku app
heroku create your-app-name

# Or connect to existing app
heroku git:remote -a existing-app-name
```

#### 2. Add PostgreSQL Database
```bash
# Add Heroku Postgres add-on
heroku addons:create heroku-postgresql:mini

# Verify database URL is set
heroku config:get DATABASE_URL
```

#### 3. Configure Environment Variables
```bash
# Set required environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY="your-secure-secret-key-here"

# Optional configurations
heroku config:set DEBUG=False
heroku config:set FLASK_DEBUG=0
```

#### 4. Deploy Application
```bash
# Deploy to Heroku
git push heroku main

# Run database migrations
heroku run python -c "from streamlined_app import db; db.create_all()"

# Optional: Load initial data
heroku run python -c "from streamlined_app import load_initial_data; load_initial_data()"
```

#### 5. Verify Deployment
```bash
# Open application
heroku open

# Check logs
heroku logs --tail

# Check application status
heroku ps
```

### Production Configuration

#### Required Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (automatically set by Heroku)
- `SECRET_KEY` - Flask secret key for session management
- `FLASK_ENV=production` - Production environment setting

#### Optional Environment Variables
- `DEBUG=False` - Disable debug mode in production
- `FLASK_DEBUG=0` - Additional debug setting
- `PORT` - Port number (automatically set by Heroku)

#### Heroku Configuration Files

**Procfile**:
```
web: gunicorn streamlined_app:app --log-file -
```

**runtime.txt**:
```
python-3.11.0
```

**requirements.txt**: (Generated via `pip freeze > requirements.txt`)

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment tool (venv or virtualenv)

### Quick Setup
```bash
# Clone repository
git clone https://github.com/adammoore/maldreth-infrastructure-interactions.git
cd maldreth-infrastructure-interactions

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python streamlined_app.py
```

Application will be available at `http://localhost:5001`

### Local Configuration

#### Environment Variables
```bash
# Development settings
export FLASK_ENV=development
export DEBUG=True
export SECRET_KEY="dev-secret-key"

# Database (SQLite for development)
export DATABASE_URL="sqlite:///instance/maldreth.db"
```

#### Database Setup
```bash
# Initialize database (automatic on first run)
python -c "from streamlined_app import db; db.create_all()"

# Load sample data
python -c "from streamlined_app import load_initial_data; load_initial_data()"
```

## Database Management

### Migration Commands
```bash
# Create database tables
python -c "from streamlined_app import db; db.create_all()"

# Drop all tables (CAUTION: Data loss!)
python -c "from streamlined_app import db; db.drop_all()"

# Recreate with fresh data
python -c "from streamlined_app import db; db.drop_all(); db.create_all()"
```

### Backup and Restore (Production)
```bash
# Create database backup
heroku pg:backups:capture --app your-app-name

# Download backup
heroku pg:backups:download --app your-app-name

# Restore backup (CAUTION)
heroku pg:backups:restore b001 DATABASE_URL --app your-app-name
```

## SSL and Security

### Heroku SSL
- SSL is automatically enabled for all `*.herokuapp.com` domains
- Custom domains require SSL certificate configuration
- Force HTTPS redirects are handled in application code

### Security Headers
Application includes security headers:
- HTTPS redirect enforcement
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options

## Monitoring and Logging

### Heroku Logs
```bash
# View recent logs
heroku logs --tail

# Filter logs
heroku logs --source app --tail
```

### Application Monitoring
- Built-in Heroku metrics available in dashboard
- Database performance metrics via Heroku Postgres
- Custom application metrics via logging

### Error Tracking
- Python exceptions logged to Heroku logs
- Database errors captured and logged
- User-facing error pages with appropriate messaging

## Performance Optimization

### Database Optimization
- Database indexes on frequently queried fields
- Connection pooling via SQLAlchemy
- Query optimization for large datasets

### Caching Strategy
- Static file caching via CDN (if configured)
- Database query result caching for expensive operations
- Browser caching headers for static assets

### Scaling Considerations
```bash
# Scale web dynos
heroku ps:scale web=2

# Upgrade database
heroku addons:upgrade heroku-postgresql:standard-0

# Add Redis for caching (optional)
heroku addons:create heroku-redis:mini
```

## Troubleshooting

### Common Issues

#### Application Won't Start
1. Check Procfile configuration
2. Verify Python version in runtime.txt
3. Ensure all dependencies in requirements.txt
4. Check environment variables

```bash
# Debug application startup
heroku logs --tail
heroku run python streamlined_app.py
```

#### Database Connection Issues
1. Verify DATABASE_URL environment variable
2. Check database add-on status
3. Ensure database tables are created

```bash
# Check database status
heroku pg:info
heroku config:get DATABASE_URL

# Test database connection
heroku run python -c "from streamlined_app import db; print(db.engine.execute('SELECT 1').scalar())"
```

#### Static Files Not Loading
1. Check static file paths in templates
2. Verify Flask static configuration
3. Ensure files exist in static/ directory

#### Performance Issues
1. Monitor database query performance
2. Check memory usage and dyno limits
3. Consider database indexing for slow queries

### Debug Mode
```bash
# Enable debug mode (development only)
heroku config:set DEBUG=True
heroku config:set FLASK_DEBUG=1

# Disable debug mode (production)
heroku config:set DEBUG=False
heroku config:set FLASK_DEBUG=0
```

### Database Reset (Development)
```bash
# Reset local database
rm instance/maldreth.db
python streamlined_app.py  # Will recreate database

# Reset production database (CAUTION)
heroku pg:reset DATABASE_URL
heroku run python -c "from streamlined_app import db; db.create_all()"
```

## CI/CD Pipeline

### Automated Deployment
- Automatic deployment on push to main branch (if configured)
- GitHub Actions integration for testing
- Automated database migrations on deployment

### Testing Pipeline
```bash
# Run tests locally
python -m pytest tests/

# Run with coverage
python -m pytest --cov=streamlined_app tests/
```

## Custom Domain Configuration

### Add Custom Domain
```bash
# Add domain to Heroku app
heroku domains:add your-domain.com

# Configure DNS with provided target
# Add CNAME record pointing to Heroku target

# Add SSL certificate
heroku certs:auto:enable
```

## Backup Strategy

### Regular Backups
```bash
# Schedule automatic backups
heroku pg:backups:schedule DATABASE_URL --at "02:00 UTC"

# Manual backup
heroku pg:backups:capture
```

### Data Export
```bash
# Export interaction data
curl https://your-app.herokuapp.com/export/interactions/csv > backup.csv

# Export tool data
curl https://your-app.herokuapp.com/api/v1/tools > tools_backup.json
```

## Support and Maintenance

### Regular Maintenance Tasks
1. Monitor application logs for errors
2. Check database performance metrics
3. Verify backup creation and retention
4. Update dependencies and security patches
5. Monitor resource usage and scaling needs

### Support Resources
- Heroku Documentation: https://devcenter.heroku.com/
- Flask Documentation: https://flask.palletsprojects.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- PRISM GitHub Issues: https://github.com/adammoore/maldreth-infrastructure-interactions/issues

For deployment support and questions, create an issue in the GitHub repository or contact the MaLDReTH II working group.