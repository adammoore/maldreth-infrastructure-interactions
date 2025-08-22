# PRISM - Platform for Research Infrastructure Synergy Mapping

[![Live Deployment](https://img.shields.io/badge/Live-Heroku-purple)](https://mal2-data-survey-cb27f6674f20.herokuapp.com/)
[![CI/CD Pipeline](https://github.com/adammoore/maldreth-infrastructure-interactions/actions/workflows/ci.yml/badge.svg)](https://github.com/adammoore/maldreth-infrastructure-interactions/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Open%20Source-green.svg)](LICENSE)

## Overview

**PRISM** (Platform for Research Infrastructure Synergy Mapping) is a comprehensive web-based platform designed to systematically map and analyze interactions between digital research tools across the research data lifecycle. As a key output of the **MaLDReTH II** (Mapping the Landscape of Digital Research Tools Harmonised) initiative under the Research Data Alliance (RDA), PRISM facilitates the collection, visualization, and analysis of tool interactions to support improved interoperability and FAIR data practices.

🌐 **Live Application**: [https://mal2-data-survey-cb27f6674f20.herokuapp.com/](https://mal2-data-survey-cb27f6674f20.herokuapp.com/)

### Key Features

- 🔄 **Interactive Tool Interaction Mapping**: Comprehensive database of research tool interactions
- 📊 **Research Data Lifecycle Visualization**: 12-stage MaLDReTH lifecycle model with tool mappings
- 📤 **CSV Import/Export**: Bulk data management with duplicate protection
- ✏️ **Curation Interface**: Edit and enhance interaction data for quality control
- 🔍 **Live Data Visualization**: Real-time statistics and analytics
- 🛡️ **Data Integrity**: Robust validation and duplicate detection
- 📱 **Responsive Design**: Works seamlessly across all devices
- 🔗 **RESTful API**: Programmatic access to all data

## MaLDReTH II Context

PRISM is an official output of the **MaLDReTH II RDA Working Group**, contributing to the Global Open Research Commons (GORC) initiative. The platform supports the working group's objectives to:

- Create a comprehensive categorisation schema for digital research tools
- Map tool interactions across the research data lifecycle
- Build an autonomous database for community curation
- Improve interoperability between research tools
- Support FAIR (Findable, Accessible, Interoperable, Reusable) data workflows

🔗 **Learn More**: [MaLDReTH II Working Group](https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (production) or SQLite (development)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/adammoore/maldreth-infrastructure-interactions.git
   cd maldreth-infrastructure-interactions
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python streamlined_app.py
   ```

5. **Access the application**
   - Open [http://localhost:5001](http://localhost:5001) in your browser
   - The database will be automatically initialized with MaLDReTH data

## Core Functionality

### 1. Interaction Management
- **Add Interactions**: Web form with tool selection and interaction details
- **View Interactions**: Comprehensive list with filtering and search
- **Edit Interactions**: Curation interface for data quality management
- **Bulk Import**: CSV upload with validation and duplicate protection

### 2. Data Visualization
- **Live Statistics**: Real-time counts and distributions
- **Interaction Analytics**: Usage patterns and tool connectivity
- **Lifecycle Mapping**: Visual representation of the 12-stage RDL model
- **Tool Networks**: Connectivity and relationship analysis

### 3. CSV Tools
- **Export**: Download complete interaction data with all fields
- **Import**: Upload CSV files with intelligent duplicate detection
- **Template**: Download current data structure as a template
- **Validation**: Tool name verification and type checking

### 4. API Access
- **REST Endpoints**: Programmatic access to all data
- **JSON Responses**: Structured data with full metadata
- **Tool Catalog**: Complete listing of available research tools
- **Interaction Data**: Full interaction details with relationships

## Database Schema

PRISM uses a hierarchical database structure designed for flexibility and extensibility:

```
MaldrethStage (12 lifecycle stages)
    ↓
ToolCategory (tool classification groups)
    ↓
ExemplarTool (267 research tools)
    ↓
ToolInteraction (tool-to-tool interactions)
```

### Core Entities

| Entity | Purpose | Key Fields |
|--------|---------|------------|
| **ToolInteraction** | Core interaction records | interaction_type, lifecycle_stage, description, technical_details |
| **ExemplarTool** | Research tools catalog | name, is_open_source, description, url |
| **ToolCategory** | Tool classification | name, description |
| **MaldrethStage** | RDL lifecycle stages | name, description, position, color |

📊 **Detailed Schema**: Visit `/information-structures` in the live application

## Demo Data

The repository includes a comprehensive demo CSV file with sample interactions:

- **File**: `demo_interactions.csv`
- **Content**: Real interactions from MaLDReTH II working sessions
- **Examples**: DMPTool-RSpace integration, Zenodo-ORCID linking, GitHub-Zenodo archiving
- **Usage**: Perfect for testing CSV import functionality

## API Reference

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tools` | GET | Complete tools catalog with metadata |
| `/api/v1/interactions` | GET | All interaction data with relationships |
| `/export/interactions/csv` | GET | CSV export of all data |
| `/upload/interactions/csv` | POST | CSV import with validation |
| `/interaction/<id>/edit` | GET/POST | Curation interface |

### Example Usage

```bash
# Get all tools
curl https://mal2-data-survey-cb27f6674f20.herokuapp.com/api/v1/tools

# Export CSV data
curl https://mal2-data-survey-cb27f6674f20.herokuapp.com/export/interactions/csv

# Get interaction statistics
curl https://mal2-data-survey-cb27f6674f20.herokuapp.com/api/v1/interactions
```

## CSV Format

PRISM supports comprehensive CSV import/export with the following structure:

### Required Fields
- `Source Tool` - Name of source tool (must exist in database)
- `Target Tool` - Name of target tool (must exist in database)  
- `Interaction Type` - Type from predefined list (API Integration, Data Exchange, etc.)
- `Lifecycle Stage` - MaLDReTH stage (PLAN, COLLECT, ANALYSE, etc.)

### Optional Fields
- `Description` - Detailed interaction description
- `Technical Details` - Implementation specifics
- `Benefits` - Advantages of the interaction
- `Challenges` - Limitations or difficulties
- `Examples` - Real-world use cases
- `Contact Person` - Subject matter expert
- `Organization` - Institution or company
- `Email` - Contact email address
- `Priority` - High/Medium/Low
- `Complexity` - Simple/Moderate/Complex
- `Status` - Proposed/Pilot/Implemented/Deprecated
- `Submitted By` - Data contributor

### Interaction Types

PRISM supports 11 predefined interaction types:
- API Integration
- Data Exchange  
- Metadata Exchange
- File Format Conversion
- Workflow Integration
- Plugin/Extension
- Direct Database Connection
- Web Service
- Command Line Interface
- Import/Export
- Other

## Deployment

### Production (Heroku)

The application is deployed on Heroku with:
- **PostgreSQL database** for data persistence
- **Automatic CI/CD** via GitHub Actions
- **Environment-based configuration**
- **Secure secret management**

### Local Development

```bash
# Quick start
python streamlined_app.py

# With specific configuration
export FLASK_ENV=development
export DATABASE_URL=sqlite:///local.db
python streamlined_app.py
```

## Contributing

PRISM welcomes contributions from the research community! Ways to contribute:

1. **Data Contribution**: Add tool interactions via the web interface or CSV upload
2. **Code Contribution**: Submit pull requests for new features or improvements
3. **Documentation**: Help improve documentation and examples
4. **Testing**: Report bugs and test new features
5. **Community**: Participate in MaLDReTH II working group discussions

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

```bash
# Run local instance
python streamlined_app.py

# Test CSV upload with demo data
# Navigate to /upload/interactions/csv and upload demo_interactions.csv

# Test API endpoints
curl http://localhost:5001/api/v1/tools | jq
```

## Technical Stack

- **Backend**: Flask (Python 3.11)
- **Database**: PostgreSQL (production), SQLite (development)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Frontend**: Bootstrap 5, Font Awesome, vanilla JavaScript
- **Deployment**: Heroku with GitHub Actions CI/CD
- **Data Processing**: Pandas for CSV handling
- **API**: RESTful JSON endpoints

## Information Structures

Visit the live **Information Structures** page for:
- Live database statistics and visualizations
- Detailed schema documentation
- CSV format specifications
- Real-time analytics and charts
- Tool usage patterns and connectivity analysis

🔗 **Access**: [Information Structures](https://mal2-data-survey-cb27f6674f20.herokuapp.com/information-structures)

## Support & Documentation

- 🌐 **Live Application**: [https://mal2-data-survey-cb27f6674f20.herokuapp.com/](https://mal2-data-survey-cb27f6674f20.herokuapp.com/)
- 📊 **About PRISM**: [/about](https://mal2-data-survey-cb27f6674f20.herokuapp.com/about)
- 🗄️ **Database Schema**: [/information-structures](https://mal2-data-survey-cb27f6674f20.herokuapp.com/information-structures)
- 🔧 **GitHub Issues**: [Report bugs or request features](https://github.com/adammoore/maldreth-infrastructure-interactions/issues)
- 📧 **Contact**: MaLDReTH II Working Group

## License

This project is open source and available under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **MaLDReTH II Working Group** and Research Data Alliance (RDA)
- **Global Open Research Commons (GORC)** initiative
- **Maria Praetzellis (CDL)** and all working session contributors
- **Flask and Python communities** for excellent frameworks and tools

---

**PRISM** is an official output of the MaLDReTH II RDA Working Group, supporting systematic mapping of research infrastructure interactions across the global research data lifecycle.

🚀 **Get Started**: [Visit PRISM](https://mal2-data-survey-cb27f6674f20.herokuapp.com/) | [Upload Data](https://mal2-data-survey-cb27f6674f20.herokuapp.com/upload/interactions/csv) | [View Documentation](https://mal2-data-survey-cb27f6674f20.herokuapp.com/information-structures)