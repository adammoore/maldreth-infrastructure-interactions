# Heroku Deployment Checklist

## Pre-Deployment Steps

1. **Clean up the project**:
   ```bash
   # Remove unnecessary files
   rm -f app.py.backup*
   rm -f fix_*.py
   rm -f *.db
   rm -rf instance/
   rm -rf __pycache__/
   ```

2. **Ensure all required files are present**:
   - ✅ `app.py` - Main application
   - ✅ `__init__.py` - App factory
   - ✅ `models.py` - Database models
   - ✅ `routes.py` - API routes
   - ✅ `init_database.py` - Database initialization
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `runtime.txt` - Python version
   - ✅ `Procfile` - Process definitions
   - ✅ `release.sh` - Release script

3. **Make release.sh executable**:
   ```bash
   chmod +x release.sh
   ```

## GitHub Setup

1. **Set up repository secrets**:
   - Go to Settings → Secrets → Actions
   - Add the following secrets:
     - `HEROKU_API_KEY` - Your Heroku API key
     - `HEROKU_APP_NAME` - Your Heroku app name
     - `HEROKU_EMAIL` - Your Heroku email

2. **Get your Heroku API key**:
   ```bash
   heroku auth:token
   ```

## Heroku Setup

1. **Create Heroku app** (if not already created):
   ```bash
   heroku create your-app-name
   ```

2. **Add PostgreSQL addon**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY="your-secret-key-here"
   heroku config:set FLASK_ENV="production"
   ```

## Deployment

1. **Commit all changes**:
   ```bash
   git add .
   git commit -m "chore: Prepare for Heroku deployment"
   ```

2. **Push to GitHub** (triggers CI/CD):
   ```bash
   git push origin main
   ```

3. **Or deploy directly to Heroku**:
   ```bash
   git push heroku main
   ```

## Post-Deployment Verification

1. **Check application logs**:
   ```bash
   heroku logs --tail
   ```

2. **Verify database initialization**:
   ```bash
   heroku run python -c "from app import create_app; from models import Stage; app = create_app(); print(f'Stages: {Stage.query.count()}')"
   ```

3. **Test the API**:
   ```bash
   # Health check
   curl https://your-app-name.herokuapp.com/api/health
   
   # Get lifecycle data
   curl https://your-app-name.herokuapp.com/api/lifecycle
   ```

## Troubleshooting

### If database is not initialized:

```bash
# Run initialization manually
heroku run python init_database.py
```

### If app crashes:

```bash
# Check logs
heroku logs --tail

# Check dyno status
heroku ps

# Restart dyno
heroku restart
```

### Common issues:

1. **Module not found**: Ensure all imports use relative imports or are in PYTHONPATH
2. **Database connection**: Check DATABASE_URL is set correctly
3. **Port binding**: Ensure app uses PORT environment variable

## Monitoring

1. **Set up alerts**:
   ```bash
   heroku alerts:add
   ```

2. **Monitor performance**:
   - Visit: https://dashboard.heroku.com/apps/your-app-name/metrics

3. **Check database**:
   ```bash
   heroku pg:info
   ```
