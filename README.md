# MaLDReTH Infrastructure Interactions

A Flask web application for collecting and managing potential infrastructure interactions for the MaLDReTH 2 Working Group meeting.

[![CI/CD Pipeline](https://github.com/adammoore/maldreth-infrastructure-interactions/actions/workflows/ci.yml/badge.svg)](https://github.com/adammoore/maldreth-infrastructure-interactions/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/adammoore/maldreth-infrastructure-interactions/branch/main/graph/badge.svg)](https://codecov.io/gh/adammoore/maldreth-infrastructure-interactions)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## 🚀 Features

- **Web Interface**: Easy-to-use forms for data collection
- **RESTful API**: Programmatic access for automation and integration
- **Data Export**: CSV export for analysis and sharing
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **PostgreSQL Support**: Production-ready database for Heroku deployment
- **Health Monitoring**: Built-in health check endpoints
- **Comprehensive Testing**: Full test suite with CI/CD integration

## 📋 Prerequisites

- **Git** installed
- **Python 3.11+** installed
- **Heroku CLI** installed (for deployment): `brew install heroku/brew/heroku` on macOS
- **Docker** (optional, for containerized development)

## 🔧 Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/adammoore/maldreth-infrastructure-interactions.git
cd maldreth-infrastructure-interactions
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 3. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your local settings
```

### 4. Initialize Database

```bash
flask init-db
```

### 5. Run the Application

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) to access the application.

## 🐳 Docker Development

For containerized development:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

## ☁️ Heroku Deployment

### Quick Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/adammoore/maldreth-infrastructure-interactions)

### Manual Deployment

```bash
# Login to Heroku
heroku login

# Create Heroku application
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY="your-production-secret-key"
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Initialize database
heroku run flask init-db

# Open application
heroku open
```

## 🔄 CI/CD Pipeline

The application includes a comprehensive CI/CD pipeline using GitHub Actions:

### Pipeline Stages

1. **Testing**: Runs pytest with coverage reporting
2. **Linting**: Code quality checks with Black, Flake8, isort, Bandit
3. **Security**: Vulnerability scanning with Trivy
4. **Build**: Application build verification
5. **Deploy**: Automatic deployment to staging/production

### GitHub Secrets Required

Set these secrets in your GitHub repository:

```
HEROKU_API_KEY=your-heroku-api-key
HEROKU_EMAIL=your-heroku-email
HEROKU_STAGING_APP_NAME=your-staging-app-name
HEROKU_PRODUCTION_APP_NAME=your-production-app-name
SLACK_WEBHOOK_URL=your-slack-webhook-url (optional)
```

### Branch Strategy

- `main`: Production deployments
- `develop`: Staging deployments
- Feature branches: Create PR to `main`

## 📊 Data Collection

The application collects the following information about infrastructure interactions:

### Core Information
- **Interaction Type**: data_flow, api_call, file_transfer, etc.
- **Source Infrastructure**: The initiating component
- **Target Infrastructure**: The receiving component
- **Lifecycle Stage**: Which stage in the research data lifecycle
- **Description**: Detailed description of the interaction

### Technical Details
- **Implementation**: Technical standards, protocols
- **Benefits**: Advantages of this interaction
- **Challenges**: Limitations or difficulties
- **Examples**: Real-world use cases

### Contact Information
- **Contact Person**: Responsible individual
- **Organization**: Associated organization
- **Email**: Contact email address

### Classification
- **Priority**: High, Medium, Low
- **Complexity**: Simple, Moderate, Complex
- **Status**: Proposed, Implemented, Deprecated

## 🔌 API Documentation

### Get All Interactions
```bash
curl https://your-app.herokuapp.com/api/interactions
```

### Create New Interaction
```bash
curl -X POST https://your-app.herokuapp.com/api/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "interaction_type": "data_flow",
    "source_infrastructure": "Research Repository",
    "target_infrastructure": "Analysis Platform",
    "lifecycle_stage": "analyse",
    "description": "Automated data transfer...",
    "priority": "high"
  }'
```

### Get Specific Interaction
```bash
curl https://your-app.herokuapp.com/api/interactions/1
```

### Health Check
```bash
curl https://your-app.herokuapp.com/health
```

## 🧪 Testing

### Run Tests Locally

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py -v

# Run with output
pytest -s
```

### Test Categories

- **Unit Tests**: Model and utility function testing
- **Integration Tests**: Route and API endpoint testing
- **Functional Tests**: End-to-end workflow testing
- **API Tests**: REST API functionality testing

## 📈 Monitoring and Maintenance

### Health Checks

The application provides health check endpoints:

- `/health`: Basic health and database connectivity
- Automatic health checks in Docker and Heroku

### Logging

- Application logs are sent to stdout/stderr
- Heroku logs: `heroku logs --tail --app your-app-name`
- Docker logs: `docker-compose logs -f web`

### Database Maintenance

```bash
# Backup database (Heroku)
heroku pg:backups:capture --app your-app-name

# Reset database
heroku run flask reset-db --app your-app-name

# Database console
heroku pg:psql --app your-app-name
```

## 💰 Cost Considerations

### Heroku Free Tier
- **Hobby Dyno**: Free for 550 hours/month
- **PostgreSQL Mini**: Free up to 10,000 rows
- **Sufficient for workshops and small deployments**

### Scaling Options
- Upgrade to Hobby ($7/month) for 24/7 availability
- Professional dynos for production workloads
- Dedicated PostgreSQL for larger datasets

## 🔍 Troubleshooting

### Common Issues

**App won't start**
```bash
heroku logs --tail --app your-app-name
# Check for missing environment variables or dependency issues
```

**Database errors**
```bash
# Ensure PostgreSQL addon is added
heroku addons --app your-app-name

# Check database connectivity
heroku run python -c "from app import db; print('DB connected')" --app your-app-name
```

**Form validation errors**
- Check browser console for JavaScript errors
- Verify all required fields are filled
- Ensure proper field formats (email, etc.)

### Getting Help

1. **Check Issues**: Search existing GitHub issues
2. **Create Issue**: Report bugs or request features
3. **Contact Team**: Reach out to MaLDReTH working group
4. **Documentation**: Review Heroku and Flask documentation

## 🔄 Updating the Application

### Local Updates
```bash
git pull origin main
pip install -r requirements.txt
flask db upgrade  # If using migrations
```

### Production Updates
```bash
git push heroku main
heroku run flask db upgrade --app your-app-name  # If using migrations
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Test** thoroughly (`pytest`)
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Create** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new functionality
- Update documentation as needed
- Use meaningful commit messages
- Ensure CI/CD pipeline passes

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This tool supports the **MaLDReTH 2 Working Group meeting** for collecting infrastructure interaction data across the research data lifecycle.

- **Working Group**: [RDA MaLDReTH](https://www.rd-alliance.org/groups/rda-ofr-mapping-landscape-digital-research-tools-wg/)
- **Documentation**: See project deliverables for context
- **Support**: Contact working group coordinators

---

**Built with ❤️ for the research data community**
