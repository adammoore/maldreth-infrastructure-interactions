# MaLDReTH Infrastructure Interactions

[![CI/CD Pipeline](https://github.com/yourusername/maldreth-infrastructure/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/maldreth-infrastructure/actions/workflows/ci.yml)
[![Coverage Status](https://codecov.io/gh/yourusername/maldreth-infrastructure/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/maldreth-infrastructure)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

The MaLDReTH (Mapping the Landscape of Digital Research Tools Harmonised) Infrastructure Interactions project is a Flask-based web application that visualizes and manages the research data lifecycle. It provides an interactive interface for exploring research tools categorized by lifecycle stages, tool categories, and their interconnections.

## Features

- 🔄 **Interactive Lifecycle Visualization**: Explore the research data lifecycle with an interactive circular diagram
- 🛠️ **Comprehensive Tool Database**: Browse and search research tools organized by stages and categories
- 📊 **Dynamic Data Management**: Add, update, and delete tools through a RESTful API
- 🔍 **Advanced Search**: Find tools quickly with full-text search capabilities
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🚀 **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ (for production)
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/maldreth-infrastructure.git
   cd maldreth-infrastructure
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Load initial data**
   ```bash
   # From Excel file
   python init_maldreth_tools.py --file data/research_data_lifecycle.xlsx
   
   # Or from CSV files
   python migrate_maldreth_data_standalone.py --csv-dir data/csv
   ```

7. **Run the application**
   ```bash
   flask run
   ```

   The application will be available at `http://localhost:5000`

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/maldreth_db
# For development, you can use SQLite
# DATABASE_URL=sqlite:///maldreth.db

# Security
CORS_ORIGINS=http://localhost:3000,http://localhost:5000

# External Services (Optional)
SENTRY_DSN=your-sentry-dsn
REDIS_URL=redis://localhost:6379

# Feature Flags
ENABLE_CACHE=true
ENABLE_RATE_LIMITING=true
```

## Usage

### Web Interface

1. **Homepage**: View the research data lifecycle overview
2. **Visualization**: Interactive circular diagram showing all stages and connections
3. **Tools Browser**: Browse and search tools by stage or category
4. **API Explorer**: Interactive API documentation at `/api/docs`

### Command Line Tools

```bash
# Initialize database with sample data
python init_maldreth_tools.py --file data/research_data_lifecycle.xlsx

# Migrate data from CSV files
python migrate_maldreth_data_standalone.py --csv-dir data/csv --clear

# Export data to JSON
flask export-data --output data/export.json

# Run database migrations
flask db upgrade
```

## API Documentation

### Authentication

The API uses token-based authentication for write operations. Include the token in the Authorization header:

```
Authorization: Bearer YOUR_API_TOKEN
```

### Endpoints

#### Lifecycle Stages

- `GET /api/lifecycle` - Get all lifecycle stages with connections
- `GET /api/stages/:id` - Get specific stage details
- `POST /api/stages` - Create new stage (requires auth)
- `PUT /api/stages/:id` - Update stage (requires auth)
- `DELETE /api/stages/:id` - Delete stage (requires auth)

#### Tools

- `GET /api/tools` - List all tools with filtering
- `GET /api/tools/:id` - Get specific tool details
- `POST /api/tools` - Create new tool (requires auth)
- `PUT /api/tools/:id` - Update tool (requires auth)
- `DELETE /api/tools/:id` - Delete tool (requires auth)
- `GET /api/search?q=query` - Search tools

#### Categories

- `GET /api/categories` - List all categories
- `GET /api/substages/:stage` - Get categories for a stage

### Example Requests

```bash
# Get all lifecycle stages
curl http://localhost:5000/api/lifecycle

# Search for tools
curl http://localhost:5000/api/search?q=miro

# Create a new tool (requires authentication)
curl -X POST http://localhost:5000/api/tools \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "New Tool",
    "description": "Tool description",
    "category_id": 1,
    "stage_id": 1
  }'
```

## Development

### Project Structure

```
maldreth-infrastructure/
├── app/
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models
│   ├── routes.py          # API routes
│   ├── utils.py           # Utility functions
│   └── templates/         # HTML templates
├── static/
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── data/             # Static data files
├── tests/
│   ├── test_app.py       # Application tests
│   ├── test_models.py    # Model tests
│   └── test_utils.py     # Utility tests
├── data/
│   ├── csv/              # CSV data files
│   └── *.xlsx            # Excel data files
├── scripts/
│   ├── init_maldreth_tools.py
│   └── migrate_maldreth_data_standalone.py
├── .github/
│   └── workflows/
│       └── ci.yml        # CI/CD pipeline
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── Procfile             # Heroku deployment
├── runtime.txt          # Python version
└── README.md            # This file
```

### Code Style

The project follows PEP 8 guidelines with the following tools:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run all checks:
```bash
make lint  # or
black . && isort . && flake8 . && mypy .
```

### Adding New Features

1. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style

3. Add tests for new functionality

4. Update documentation

5. Submit a pull request

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v

# Run only marked tests
pytest -m "not slow"
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **API Tests**: Test REST endpoints
- **UI Tests**: Test user interface (if applicable)

### Writing Tests

```python
# Example test
def test_create_tool(client, sample_data):
    """Test creating a new tool."""
    response = client.post('/api/tools', json={
        'name': 'Test Tool',
        'category_id': 1,
        'stage_id': 1
    })
    assert response.status_code == 201
    assert response.json['name'] == 'Test Tool'
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment.

### Pipeline Stages

1. **Lint**: Code quality checks
   - flake8 for Python linting
   - black for code formatting
   - isort for import sorting

2. **Test**: Automated testing
   - Unit tests with pytest
   - Coverage reporting with codecov
   - Database tests with PostgreSQL

3. **Security**: Security scanning
   - Safety check for vulnerable dependencies
   - Bandit for security issues in code

4. **Build**: Application packaging
   - Collect static files
   - Create deployment artifact

5. **Deploy**: Automatic deployment
   - Deploy to Heroku on main branch
   - Run database migrations
   - Send notifications

### Setting up CI/CD

1. **GitHub Secrets**: Add the following secrets to your repository
   - `HEROKU_API_KEY`: Your Heroku API key
   - `HEROKU_APP_NAME`: Your Heroku app name
   - `HEROKU_EMAIL`: Your Heroku account email
   - `SECRET_KEY`: Flask secret key
   - `SLACK_WEBHOOK`: (Optional) Slack webhook for notifications

2. **Branch Protection**: Enable branch protection rules for `main`
   - Require pull request reviews
   - Require status checks to pass
   - Include administrators

3. **Deployment**: Pushes to `main` trigger automatic deployment

## Deployment

### Heroku Deployment

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Add PostgreSQL addon**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. **Set environment variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Run migrations**
   ```bash
   heroku run flask db upgrade
   ```

6. **Load initial data**
   ```bash
   heroku run python init_maldreth_tools.py
   ```

### Docker Deployment

```bash
# Build image
docker build -t maldreth-app .

# Run container
docker run -p 5000:5000 -e DATABASE_URL=your-db-url maldreth-app
```

### Production Considerations

- Use a production WSGI server (gunicorn)
- Enable SSL/TLS
- Set up monitoring (Sentry, New Relic)
- Configure backups for the database
- Use a CDN for static files
- Implement rate limiting
- Set up logging aggregation

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

### Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The MaLDReTH Working Group for the research data lifecycle model
- All contributors who have helped shape this project
- The Flask and Python communities for excellent tools and libraries

## Support

- **Documentation**: [https://maldreth-docs.readthedocs.io](https://maldreth-docs.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/yourusername/maldreth-infrastructure/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/maldreth-infrastructure/discussions)
- **Email**: support@maldreth.org

---

Made with ❤️ by the MaLDReTH Development Team
