# Phase 1: Detailed Implementation Plan
**PRISM Usability Improvements - Immediate Fixes (Week 1-2)**

**Project**: Platform for Research Infrastructure Synergy Mapping (PRISM)
**Phase**: 1 of 5
**Timeline**: 10 working days
**Branch Strategy**: Feature branches merged to main after review
**Status**: Ready for implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites & Setup](#prerequisites--setup)
3. [Feature 1.1: Interaction Type Definitions & Glossary](#feature-11-interaction-type-definitions--glossary)
4. [Feature 1.2: Inline Tooltips and Help](#feature-12-inline-tooltips-and-help)
5. [Feature 1.3: Tool Search/Autocomplete](#feature-13-tool-searchautocomplete)
6. [Feature 1.4: CSV Template Download](#feature-14-csv-template-download)
7. [Feature 1.5: Basic Search Functionality](#feature-15-basic-search-functionality)
8. [Testing Protocol](#testing-protocol)
9. [Deployment Checklist](#deployment-checklist)
10. [Rollback Plan](#rollback-plan)

---

## Overview

### Objectives
- Improve user onboarding and reduce confusion ("too many categories")
- Provide clear definitions for all interaction types and terminology
- Enable efficient tool discovery and search
- Maintain 100% backward compatibility with existing data and features

### Success Criteria
- All 21 existing HTML templates continue to function
- All current routes remain operational
- Database schema unchanged (no migrations required)
- Existing interactions and tools remain intact
- Performance maintained or improved

### Risk Mitigation
- Feature flags for easy rollback
- Comprehensive backup before deployment
- Staged implementation with testing between features
- Human review checkpoints at critical junctures

---

## Prerequisites & Setup

### Development Environment

**Required Software:**
- Python 3.11+
- PostgreSQL (production) or SQLite (development)
- Git
- Modern web browser (Chrome, Firefox, Safari, Edge)

**Setup Steps:**

```bash
# 1. Create feature branch
git checkout -b phase-1-usability-improvements

# 2. Backup current database (CRITICAL)
# For SQLite (development):
cp streamlined_maldreth.db streamlined_maldreth.db.backup.$(date +%Y%m%d_%H%M%S)

# For PostgreSQL (production):
# heroku pg:backups:capture --app mal2-data-survey-cb27f6674f20

# 3. Verify current state
python streamlined_app.py
# Navigate to http://localhost:5001 and verify all pages load

# 4. Run existing tests (if any)
# pytest tests/ -v

# 5. Document current route count
grep -n "@app.route" streamlined_app.py | wc -l
# Expected output: 16-20 routes
```

### 🔴 HUMAN REVIEW CHECKPOINT 1: Environment Setup
**Reviewer Actions:**
- [ ] Confirm backup created successfully
- [ ] Verify current application runs without errors
- [ ] Check all existing routes accessible
- [ ] Document any existing bugs or issues (to avoid false attribution)
- [ ] Sign off on proceeding to implementation

**Sign-off:** _________________ Date: _________

---

## Feature 1.1: Interaction Type Definitions & Glossary

**Priority**: CRITICAL
**Estimated Time**: 4-6 hours
**Dependencies**: None
**Backward Compatibility**: 100% - No existing features affected

### Implementation Steps

#### Step 1.1.1: Create Interaction Type Definitions Dictionary

**File**: `streamlined_app.py`
**Action**: Add after line 59 (after LIFECYCLE_STAGES definition)

```python
# Add this constant dictionary
INTERACTION_TYPE_DEFINITIONS = {
    'API Integration': {
        'definition': 'Direct programmatic connection between tools using Application Programming Interfaces',
        'example': 'DMPTool connects to RSpace via REST API to sync data management plans',
        'when_to_use': 'When tools communicate programmatically with structured data exchange',
        'technical_indicators': ['REST API', 'GraphQL', 'SOAP', 'JSON', 'XML', 'OAuth'],
        'common_protocols': ['HTTP/HTTPS', 'REST', 'SOAP', 'gRPC']
    },
    'Data Exchange': {
        'definition': 'Transfer of research data files or datasets between tools',
        'example': 'Zenodo receives data files exported from GitHub repositories',
        'when_to_use': 'When the primary function is moving data content between systems',
        'technical_indicators': ['file transfer', 'bulk data', 'datasets', 'repository sync'],
        'common_protocols': ['FTP', 'SFTP', 'rsync', 'cloud storage APIs']
    },
    'Metadata Exchange': {
        'definition': 'Transfer of descriptive information about data without moving the data itself',
        'example': 'ORCID profile information linked to publications in Zenodo',
        'when_to_use': 'When exchanging descriptions, citations, or contextual information',
        'technical_indicators': ['metadata', 'schema', 'descriptive info', 'catalog'],
        'common_protocols': ['OAI-PMH', 'SWORD', 'Dublin Core', 'DataCite']
    },
    'File Format Conversion': {
        'definition': 'Transformation of data from one file format to another',
        'example': 'Converting CSV data to Parquet format for analysis',
        'when_to_use': 'When format transformation is the primary interaction purpose',
        'technical_indicators': ['format change', 'conversion', 'transformation', 'encoding'],
        'common_formats': ['CSV', 'JSON', 'XML', 'Parquet', 'HDF5', 'NetCDF']
    },
    'Workflow Integration': {
        'definition': 'Tools combined into multi-step research workflows or pipelines',
        'example': 'Jupyter Notebook packaged with Docker for reproducible analysis',
        'when_to_use': 'When tools are orchestrated together in a sequence',
        'technical_indicators': ['pipeline', 'workflow', 'orchestration', 'automation'],
        'common_tools': ['Airflow', 'Nextflow', 'Snakemake', 'Galaxy', 'Taverna']
    },
    'Plugin/Extension': {
        'definition': 'One tool extends functionality of another through add-ons or plugins',
        'example': 'Zotero plugin installed in Microsoft Word for citation management',
        'when_to_use': 'When one tool adds features directly into another tool\'s interface',
        'technical_indicators': ['plugin', 'extension', 'add-on', 'module'],
        'common_patterns': ['Browser extensions', 'IDE plugins', 'Office add-ins']
    },
    'Direct Database Connection': {
        'definition': 'Tools query or write to shared database infrastructure',
        'example': 'Analysis tool connects directly to PostgreSQL research database',
        'when_to_use': 'When tools share underlying data storage layer',
        'technical_indicators': ['database', 'SQL', 'NoSQL', 'direct connection'],
        'common_databases': ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch']
    },
    'Web Service': {
        'definition': 'Tools interact via web-based service endpoints (may include APIs)',
        'example': 'Data repository accessed via OAI-PMH harvesting protocol',
        'when_to_use': 'For web-protocol-based interactions like HTTP, SOAP, OAI-PMH',
        'technical_indicators': ['web service', 'endpoint', 'WSDL', 'service oriented'],
        'common_protocols': ['HTTP', 'SOAP', 'XML-RPC', 'OAI-PMH']
    },
    'Command Line Interface': {
        'definition': 'Tools invoked or controlled via terminal commands or scripts',
        'example': 'Python script calls FFmpeg via command line to process video data',
        'when_to_use': 'When interaction happens through shell commands or scripts',
        'technical_indicators': ['CLI', 'bash', 'shell script', 'command line'],
        'common_contexts': ['Batch processing', 'Automation scripts', 'HPC jobs']
    },
    'Import/Export': {
        'definition': 'Manual or semi-automated file-based data transfer between tools',
        'example': 'Export CSV from REDCap, import into R for analysis',
        'when_to_use': 'When users manually transfer files between systems',
        'technical_indicators': ['export', 'import', 'download', 'upload', 'manual transfer'],
        'common_formats': ['CSV', 'Excel', 'JSON', 'XML', 'text files']
    },
    'Other': {
        'definition': 'Interaction types not covered by standard categories',
        'example': 'Custom or novel integration approaches',
        'when_to_use': 'When no other category fits; please describe in Technical Details',
        'technical_indicators': ['custom', 'proprietary', 'novel', 'unique'],
        'note': 'Please provide detailed description to help us improve categorization'
    }
}

# Add lifecycle stage detailed definitions
LIFECYCLE_STAGE_DEFINITIONS = {
    'CONCEPTUALISE': {
        'definition': 'Initial research idea formation and hypothesis development',
        'activities': ['Literature review', 'Hypothesis formation', 'Research question development'],
        'typical_tools': ['Reference managers', 'Mind mapping tools', 'Literature databases'],
        'duration': 'Weeks to months',
        'outputs': ['Research questions', 'Hypotheses', 'Initial concepts']
    },
    'PLAN': {
        'definition': 'Research design, methodology planning, and resource allocation',
        'activities': ['Study design', 'Protocol development', 'Resource planning', 'DMP creation'],
        'typical_tools': ['DMP tools', 'Project management', 'Protocol repositories'],
        'duration': 'Weeks to months',
        'outputs': ['Data Management Plans', 'Protocols', 'Study designs']
    },
    'FUND': {
        'definition': 'Grant applications and resource acquisition',
        'activities': ['Grant writing', 'Budget planning', 'Proposal submission'],
        'typical_tools': ['Grant management systems', 'Budget calculators', 'Proposal tools'],
        'duration': 'Months to years',
        'outputs': ['Grant proposals', 'Budgets', 'Funding awards']
    },
    'COLLECT': {
        'definition': 'Data gathering and experimental execution',
        'activities': ['Experiments', 'Surveys', 'Observations', 'Measurements', 'Sampling'],
        'typical_tools': ['Lab instruments', 'Survey platforms', 'Sensors', 'Data loggers'],
        'duration': 'Days to years',
        'outputs': ['Raw data', 'Observations', 'Measurements', 'Samples']
    },
    'PROCESS': {
        'definition': 'Data cleaning, quality control, and preparation',
        'activities': ['Data cleaning', 'Quality assurance', 'Normalization', 'Format conversion'],
        'typical_tools': ['Data cleaning tools', 'ETL platforms', 'Quality control software'],
        'duration': 'Days to months',
        'outputs': ['Cleaned datasets', 'Quality reports', 'Processed data']
    },
    'ANALYSE': {
        'definition': 'Statistical analysis and interpretation',
        'activities': ['Statistical tests', 'Modeling', 'Visualization', 'Pattern discovery'],
        'typical_tools': ['R', 'Python', 'SPSS', 'MATLAB', 'Jupyter', 'Statistical software'],
        'duration': 'Weeks to months',
        'outputs': ['Analysis results', 'Statistical models', 'Visualizations']
    },
    'STORE': {
        'definition': 'Short-term data storage during active research',
        'activities': ['Active storage', 'Backup', 'Version control', 'Collaboration'],
        'typical_tools': ['Cloud storage', 'Version control', 'Lab servers', 'Collaborative platforms'],
        'duration': 'Duration of project',
        'outputs': ['Backed up data', 'Version history', 'Shared datasets']
    },
    'PUBLISH': {
        'definition': 'Dissemination through journals, conferences, preprints',
        'activities': ['Paper writing', 'Peer review', 'Conference presentations', 'Preprints'],
        'typical_tools': ['Journal systems', 'Preprint servers', 'Writing tools', 'LaTeX'],
        'duration': 'Months to years',
        'outputs': ['Publications', 'Presentations', 'Preprints']
    },
    'PRESERVE': {
        'definition': 'Long-term archival and curation',
        'activities': ['Archiving', 'Format migration', 'Metadata enrichment', 'Curation'],
        'typical_tools': ['Repositories', 'Archives', 'Preservation systems', 'Digital curation'],
        'duration': 'Permanent',
        'outputs': ['Archived datasets', 'DOIs', 'Preserved research outputs']
    },
    'SHARE': {
        'definition': 'Making data accessible to others',
        'activities': ['Publishing datasets', 'Access control', 'License assignment', 'Documentation'],
        'typical_tools': ['Data repositories', 'Institutional repositories', 'Figshare', 'Zenodo'],
        'duration': 'Ongoing',
        'outputs': ['Shared datasets', 'Data publications', 'Access portals']
    },
    'ACCESS': {
        'definition': 'Discovery and retrieval of data by users',
        'activities': ['Data discovery', 'Search', 'Download', 'API access'],
        'typical_tools': ['Data catalogs', 'Search engines', 'Repository interfaces', 'APIs'],
        'duration': 'Ongoing',
        'outputs': ['Downloaded data', 'Retrieved datasets', 'Access logs']
    },
    'TRANSFORM': {
        'definition': 'Data reuse, repurposing, and derivative works',
        'activities': ['Data reuse', 'Integration', 'Meta-analysis', 'Derivative creation'],
        'typical_tools': ['Analysis tools', 'Integration platforms', 'Synthesis tools'],
        'duration': 'Varies',
        'outputs': ['Derived datasets', 'Integrated data', 'Meta-analyses']
    }
}
```

**Preservation Check:**
- ✅ No modification to existing INTERACTION_TYPES list
- ✅ No modification to existing LIFECYCLE_STAGES list
- ✅ Purely additive - adds new dictionaries
- ✅ No database changes required
- ✅ Backward compatible - existing code unaffected

#### Step 1.1.2: Create Glossary Route

**File**: `streamlined_app.py`
**Action**: Add new route (after existing routes, around line 600)

```python
@app.route('/glossary')
def glossary():
    """Comprehensive glossary and terminology reference page."""
    try:
        # Get all stages with their definitions
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()

        # Get statistics for context
        total_interactions = ToolInteraction.query.count()
        total_tools = ExemplarTool.query.count()

        # Get interaction type usage statistics
        interaction_type_stats = {}
        for itype in INTERACTION_TYPES:
            count = ToolInteraction.query.filter_by(interaction_type=itype).count()
            interaction_type_stats[itype] = count

        return render_template('glossary.html',
                             interaction_types=INTERACTION_TYPE_DEFINITIONS,
                             lifecycle_stages=LIFECYCLE_STAGE_DEFINITIONS,
                             stages=stages,
                             interaction_type_stats=interaction_type_stats,
                             total_interactions=total_interactions,
                             total_tools=total_tools)
    except Exception as e:
        logger.error(f"Error in glossary route: {e}")
        return render_template('error.html', error=str(e)), 500
```

**Preservation Check:**
- ✅ New route, doesn't modify existing routes
- ✅ Uses existing models (MaldrethStage, ToolInteraction, ExemplarTool)
- ✅ No database modifications
- ✅ Uses error.html template (already exists)

#### Step 1.1.3: Create Glossary Template

**File**: `templates/glossary.html` (NEW FILE)
**Action**: Create comprehensive glossary page

```html
{% extends "streamlined_base.html" %}

{% block title %}Glossary - PRISM{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-lg-10 mx-auto">
            <!-- Header -->
            <div class="text-center mb-5">
                <h1 class="display-4 text-primary mb-3">
                    <i class="fas fa-book me-3"></i>PRISM Glossary
                </h1>
                <p class="lead text-muted">
                    Comprehensive definitions and guidance for using the Platform for Research Infrastructure Synergy Mapping
                </p>
            </div>

            <!-- Quick Navigation -->
            <div class="card border-0 shadow-sm mb-4">
                <div class="card-body">
                    <h5 class="card-title">Quick Navigation</h5>
                    <div class="row">
                        <div class="col-md-4">
                            <ul class="list-unstyled">
                                <li><a href="#interaction-types"><i class="fas fa-link me-2"></i>Interaction Types</a></li>
                                <li><a href="#lifecycle-stages"><i class="fas fa-recycle me-2"></i>Lifecycle Stages</a></li>
                            </ul>
                        </div>
                        <div class="col-md-4">
                            <ul class="list-unstyled">
                                <li><a href="#maldreth-terms"><i class="fas fa-project-diagram me-2"></i>MaLDReTH Terms</a></li>
                                <li><a href="#technical-terms"><i class="fas fa-code me-2"></i>Technical Terms</a></li>
                            </ul>
                        </div>
                        <div class="col-md-4">
                            <ul class="list-unstyled">
                                <li><a href="#contributing"><i class="fas fa-hands-helping me-2"></i>Contributing Guide</a></li>
                                <li><a href="#faq"><i class="fas fa-question-circle me-2"></i>FAQ</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Interaction Types Section -->
            <div id="interaction-types" class="mb-5">
                <h2 class="border-bottom pb-3 mb-4">
                    <i class="fas fa-link me-2 text-primary"></i>Interaction Types
                </h2>
                <p class="lead">
                    PRISM categorizes tool interactions into {{ interaction_types|length }} distinct types.
                    Understanding these helps you accurately describe how research tools connect and communicate.
                </p>

                {% for type_name, type_info in interaction_types.items() %}
                <div class="card mb-3 border-0 shadow-sm">
                    <div class="card-header bg-light">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h4 class="mb-0 text-primary">{{ type_name }}</h4>
                            </div>
                            <div class="col-md-4 text-end">
                                <span class="badge bg-info">
                                    {{ interaction_type_stats.get(type_name, 0) }} interactions
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <p class="mb-2"><strong>Definition:</strong></p>
                                <p>{{ type_info.definition }}</p>

                                <p class="mb-2 mt-3"><strong>When to use:</strong></p>
                                <p class="text-muted">{{ type_info.when_to_use }}</p>

                                <p class="mb-2 mt-3"><strong>Example:</strong></p>
                                <div class="alert alert-success border-0 mb-0">
                                    <i class="fas fa-lightbulb me-2"></i>{{ type_info.example }}
                                </div>
                            </div>
                            <div class="col-md-4">
                                {% if type_info.technical_indicators %}
                                <p class="mb-2"><strong>Technical Indicators:</strong></p>
                                <div class="d-flex flex-wrap gap-1 mb-3">
                                    {% for indicator in type_info.technical_indicators %}
                                    <span class="badge bg-secondary">{{ indicator }}</span>
                                    {% endfor %}
                                </div>
                                {% endif %}

                                {% if type_info.get('common_protocols') or type_info.get('common_tools') or type_info.get('common_formats') or type_info.get('common_databases') or type_info.get('common_patterns') or type_info.get('common_contexts') %}
                                <p class="mb-2"><strong>Common Technologies:</strong></p>
                                <ul class="small">
                                    {% for item in type_info.get('common_protocols', []) + type_info.get('common_tools', []) + type_info.get('common_formats', []) + type_info.get('common_databases', []) + type_info.get('common_patterns', []) + type_info.get('common_contexts', []) %}
                                    <li>{{ item }}</li>
                                    {% endfor %}
                                </ul>
                                {% endif %}

                                {% if type_info.get('note') %}
                                <div class="alert alert-warning border-0 small">
                                    <i class="fas fa-exclamation-triangle me-1"></i>{{ type_info.note }}
                                </div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- Lifecycle Stages Section -->
            <div id="lifecycle-stages" class="mb-5">
                <h2 class="border-bottom pb-3 mb-4">
                    <i class="fas fa-recycle me-2 text-primary"></i>Research Data Lifecycle Stages
                </h2>
                <p class="lead">
                    The MaLDReTH model defines 12 stages in the research data lifecycle,
                    representing the complete journey of research data from conception to reuse.
                </p>

                <div class="alert alert-info border-0 mb-4">
                    <h5 class="alert-heading">About the 12-Stage Model</h5>
                    <p class="mb-0">
                        This lifecycle model was developed by the MaLDReTH II RDA Working Group to provide
                        a comprehensive framework for understanding research data workflows. The stages are
                        sequential but can also be iterative and overlapping in practice.
                    </p>
                </div>

                {% for stage_name, stage_info in lifecycle_stages.items() %}
                {% set stage_obj = stages|selectattr('name', 'equalto', stage_name)|first %}
                <div class="card mb-3 border-0 shadow-sm">
                    <div class="card-header" style="background-color: {{ stage_obj.color if stage_obj else '#007bff' }}20;">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h4 class="mb-0">
                                    <span class="badge" style="background-color: {{ stage_obj.color if stage_obj else '#007bff' }};">
                                        {{ stage_obj.position + 1 if stage_obj else '?' }}
                                    </span>
                                    {{ stage_name }}
                                </h4>
                            </div>
                            <div class="col-md-4 text-end">
                                <span class="badge bg-secondary">
                                    Duration: {{ stage_info.duration }}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <p><strong>Definition:</strong> {{ stage_info.definition }}</p>

                        <div class="row mt-3">
                            <div class="col-md-6">
                                <p class="mb-2"><strong>Key Activities:</strong></p>
                                <ul>
                                    {% for activity in stage_info.activities %}
                                    <li>{{ activity }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <p class="mb-2"><strong>Typical Outputs:</strong></p>
                                <ul>
                                    {% for output in stage_info.outputs %}
                                    <li>{{ output }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>

                        <div class="alert alert-light border-0 mt-3 mb-0">
                            <p class="mb-1"><strong>Typical Tools:</strong></p>
                            <p class="mb-0 text-muted">{{ stage_info.typical_tools|join(', ') }}</p>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- MaLDReTH Terminology -->
            <div id="maldreth-terms" class="mb-5">
                <h2 class="border-bottom pb-3 mb-4">
                    <i class="fas fa-project-diagram me-2 text-primary"></i>MaLDReTH Terminology
                </h2>

                <dl class="row">
                    <dt class="col-sm-3">MaLDReTH</dt>
                    <dd class="col-sm-9">
                        <strong>M</strong>apping the <strong>L</strong>andscape of <strong>D</strong>igital
                        <strong>Re</strong>search <strong>T</strong>ools <strong>H</strong>armonised.
                        An RDA Working Group initiative focused on creating a comprehensive categorization
                        schema for digital research tools.
                    </dd>

                    <dt class="col-sm-3">PRISM</dt>
                    <dd class="col-sm-9">
                        <strong>P</strong>latform for <strong>R</strong>esearch <strong>I</strong>nfrastructure
                        <strong>S</strong>ynergy <strong>M</strong>apping. This web application - a key output
                        of the MaLDReTH II initiative.
                    </dd>

                    <dt class="col-sm-3">Exemplar Tool</dt>
                    <dd class="col-sm-9">
                        A representative tool within a category, demonstrating typical characteristics
                        and capabilities. Currently PRISM contains {{ total_tools }} exemplar tools.
                    </dd>

                    <dt class="col-sm-3">Tool Category</dt>
                    <dd class="col-sm-9">
                        A classification group for similar tools within a lifecycle stage. Categories help
                        organize tools by function and purpose.
                    </dd>

                    <dt class="col-sm-3">Tool Interaction</dt>
                    <dd class="col-sm-9">
                        A connection or integration between two research tools, describing how they
                        communicate or work together. PRISM currently contains {{ total_interactions }}
                        documented interactions.
                    </dd>

                    <dt class="col-sm-3">Research Data Lifecycle (RDL)</dt>
                    <dd class="col-sm-9">
                        The 12-stage model describing the complete journey of research data from initial
                        concept through to reuse and transformation.
                    </dd>

                    <dt class="col-sm-3">GORC</dt>
                    <dd class="col-sm-9">
                        <strong>G</strong>lobal <strong>O</strong>pen <strong>R</strong>esearch
                        <strong>C</strong>ommons. An RDA initiative that PRISM contributes to, focused on
                        improving interoperability and FAIR data practices.
                    </dd>
                </dl>
            </div>

            <!-- Technical Terms -->
            <div id="technical-terms" class="mb-5">
                <h2 class="border-bottom pb-3 mb-4">
                    <i class="fas fa-code me-2 text-primary"></i>Technical Terms
                </h2>

                <div class="row">
                    <div class="col-md-6">
                        <dl>
                            <dt>API</dt>
                            <dd><strong>A</strong>pplication <strong>P</strong>rogramming <strong>I</strong>nterface.
                            A set of protocols for building software and enabling tool-to-tool communication.</dd>

                            <dt>REST</dt>
                            <dd><strong>RE</strong>presentational <strong>S</strong>tate <strong>T</strong>ransfer.
                            An architectural style for web APIs using HTTP methods.</dd>

                            <dt>OAuth</dt>
                            <dd><strong>O</strong>pen <strong>Auth</strong>orization. A standard for secure
                            authorization and authentication between applications.</dd>

                            <dt>DOI</dt>
                            <dd><strong>D</strong>igital <strong>O</strong>bject <strong>I</strong>dentifier.
                            A persistent identifier for digital objects like datasets and publications.</dd>

                            <dt>ORCID</dt>
                            <dd><strong>O</strong>pen <strong>R</strong>esearcher and <strong>C</strong>ontributor
                            <strong>ID</strong>. A unique identifier for researchers and scholars.</dd>
                        </dl>
                    </div>
                    <div class="col-md-6">
                        <dl>
                            <dt>FAIR</dt>
                            <dd><strong>F</strong>indable, <strong>A</strong>ccessible, <strong>I</strong>nteroperable,
                            <strong>R</strong>eusable. Principles for scientific data management and stewardship.</dd>

                            <dt>OAI-PMH</dt>
                            <dd><strong>O</strong>pen <strong>A</strong>rchives <strong>I</strong>nitiative
                            <strong>P</strong>rotocol for <strong>M</strong>etadata <strong>H</strong>arvesting.
                            A protocol for sharing metadata between repositories.</dd>

                            <dt>JSON</dt>
                            <dd><strong>J</strong>ava<strong>S</strong>cript <strong>O</strong>bject
                            <strong>N</strong>otation. A lightweight data format for API communication.</dd>

                            <dt>CSV</dt>
                            <dd><strong>C</strong>omma-<strong>S</strong>eparated <strong>V</strong>alues.
                            A simple file format for tabular data exchange.</dd>

                            <dt>CLI</dt>
                            <dd><strong>C</strong>ommand <strong>L</strong>ine <strong>I</strong>nterface.
                            Text-based interface for interacting with software via commands.</dd>
                        </dl>
                    </div>
                </div>
            </div>

            <!-- Contributing Guide -->
            <div id="contributing" class="mb-5">
                <h2 class="border-bottom pb-3 mb-4">
                    <i class="fas fa-hands-helping me-2 text-primary"></i>Contributing to PRISM
                </h2>

                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h5>How to Add an Interaction</h5>
                        <ol>
                            <li><strong>Identify the tools:</strong> Determine the source and target tools involved</li>
                            <li><strong>Select interaction type:</strong> Review the definitions above to choose the most appropriate type</li>
                            <li><strong>Choose lifecycle stage:</strong> Identify which research stage this interaction supports</li>
                            <li><strong>Describe the interaction:</strong> Write 1-3 sentences explaining what happens and why it's useful</li>
                            <li><strong>Add technical details:</strong> Include protocols, APIs, or technologies used (optional but recommended)</li>
                            <li><strong>Provide examples:</strong> Share real-world use cases (optional but valuable)</li>
                        </ol>
                    </div>
                </div>

                <div class="card border-0 shadow-sm mb-3">
                    <div class="card-body">
                        <h5>What Makes a Good Interaction Description</h5>
                        <ul>
                            <li><strong>Clear and specific:</strong> Explain exactly what the interaction does</li>
                            <li><strong>Accurate categorization:</strong> Use the correct interaction type and lifecycle stage</li>
                            <li><strong>Technical depth:</strong> Include implementation details when known</li>
                            <li><strong>Real examples:</strong> Reference actual use cases or institutions</li>
                            <li><strong>Benefits and challenges:</strong> Help others understand trade-offs</li>
                        </ul>
                    </div>
                </div>

                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <h5>Bulk Upload via CSV</h5>
                        <p>For adding multiple interactions:</p>
                        <ol>
                            <li>Download the <a href="{{ url_for('export_csv') }}">CSV template</a> to see the format</li>
                            <li>Prepare your data following the same structure</li>
                            <li>Ensure tool names match existing tools in PRISM (or new tools will be created)</li>
                            <li>Use the <a href="{{ url_for('upload_csv') }}">CSV upload page</a> to submit your file</li>
                            <li>Review the results and fix any errors reported</li>
                        </ol>
                    </div>
                </div>
            </div>

            <!-- FAQ -->
            <div id="faq" class="mb-5">
                <h2 class="border-bottom pb-3 mb-4">
                    <i class="fas fa-question-circle me-2 text-primary"></i>Frequently Asked Questions
                </h2>

                <div class="accordion" id="faqAccordion">
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#faq1">
                                What is the difference between "API Integration" and "Web Service"?
                            </button>
                        </h2>
                        <div id="faq1" class="accordion-collapse collapse show" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                <strong>API Integration</strong> refers to modern RESTful or GraphQL APIs with programmatic access,
                                typically using JSON. <strong>Web Service</strong> is broader and includes older protocols like
                                SOAP, XML-RPC, or domain-specific protocols like OAI-PMH. If in doubt, "API Integration" is
                                usually the better choice for contemporary tools.
                            </div>
                        </div>
                    </div>

                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">
                                Can one interaction belong to multiple lifecycle stages?
                            </button>
                        </h2>
                        <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                Currently, each interaction is assigned to one primary lifecycle stage. If an interaction
                                genuinely supports multiple stages, choose the stage where it's most commonly used, and mention
                                the other stages in the description or examples field.
                            </div>
                        </div>
                    </div>

                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq3">
                                What if the tools I want to add aren't in PRISM yet?
                            </button>
                        </h2>
                        <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                When you add an interaction via CSV upload, PRISM will automatically create any missing tools.
                                For manual entry through the web form, please contact the MaLDReTH II working group to request
                                tool additions, or use the CSV bulk upload feature.
                            </div>
                        </div>
                    </div>

                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq4">
                                How is PRISM different from other tool catalogs?
                            </button>
                        </h2>
                        <div id="faq4" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                PRISM focuses specifically on <strong>interactions between tools</strong> rather than just
                                cataloging individual tools. While many catalogs list research tools, PRISM maps how they
                                connect, integrate, and work together across the research data lifecycle. This makes it
                                uniquely valuable for understanding research infrastructure interoperability.
                            </div>
                        </div>
                    </div>

                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq5">
                                Can I edit or update an interaction I submitted?
                            </button>
                        </h2>
                        <div id="faq5" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                Yes! Every interaction has an "Edit" button on its detail page. You can update any field
                                to improve accuracy or add additional information. All edits help improve the quality of
                                PRISM's knowledge base.
                            </div>
                        </div>
                    </div>

                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq6">
                                Who maintains PRISM and how can I get involved?
                            </button>
                        </h2>
                        <div id="faq6" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                PRISM is maintained by the <a href="https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii" target="_blank">
                                MaLDReTH II RDA Working Group</a>. You can get involved by:
                                <ul class="mt-2">
                                    <li>Contributing interaction data through PRISM</li>
                                    <li>Joining the MaLDReTH II working group</li>
                                    <li>Participating in RDA plenary sessions</li>
                                    <li>Providing feedback and suggestions</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Call to Action -->
            <div class="card border-0 shadow bg-primary text-white">
                <div class="card-body text-center py-4">
                    <h3 class="mb-3">Ready to Contribute?</h3>
                    <p class="mb-4">Use your new knowledge to help map the research infrastructure landscape</p>
                    <div class="d-flex gap-3 justify-content-center flex-wrap">
                        <a href="{{ url_for('add_interaction') }}" class="btn btn-light btn-lg">
                            <i class="fas fa-plus me-2"></i>Add Interaction
                        </a>
                        <a href="{{ url_for('view_interactions') }}" class="btn btn-outline-light btn-lg">
                            <i class="fas fa-list me-2"></i>Browse Interactions
                        </a>
                        <a href="{{ url_for('about') }}" class="btn btn-outline-light btn-lg">
                            <i class="fas fa-info-circle me-2"></i>About PRISM
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Back to Top Button -->
<a href="#" class="btn btn-primary position-fixed bottom-0 end-0 m-4" style="z-index: 1000;">
    <i class="fas fa-arrow-up"></i>
</a>
{% endblock %}
```

**Preservation Check:**
- ✅ Extends streamlined_base.html (existing template)
- ✅ Uses existing URL routing functions (url_for)
- ✅ No JavaScript dependencies beyond Bootstrap (already loaded)
- ✅ Responsive design using existing Bootstrap classes

#### Step 1.1.4: Add Navigation Link

**File**: `templates/streamlined_base.html`
**Action**: Add glossary link to navigation menu

**Before making changes, locate the navigation section:**
```bash
grep -n "nav-link" templates/streamlined_base.html
```

**Add after existing nav items** (typically around line 30-50):
```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('glossary') }}">
        <i class="fas fa-book me-1"></i>Glossary
    </a>
</li>
```

**Preservation Check:**
- ✅ Additive only - adds new nav item
- ✅ Uses existing nav-item and nav-link classes
- ✅ Follows existing pattern (icon + text)
- ✅ No modification to existing nav items

### 🔴 HUMAN REVIEW CHECKPOINT 2: Feature 1.1 Complete
**Reviewer Actions:**
- [ ] Review glossary definitions for accuracy
- [ ] Check lifecycle stage descriptions align with MaLDReTH II documentation
- [ ] Verify no existing routes broken
- [ ] Test glossary page renders correctly
- [ ] Confirm navigation link appears and works
- [ ] Validate all examples are appropriate
- [ ] Test on mobile and desktop views

**Testing Commands:**
```bash
# Start application
python streamlined_app.py

# Test glossary route
curl http://localhost:5001/glossary | grep "Glossary"

# Verify existing routes still work
curl http://localhost:5001/ | grep "PRISM"
curl http://localhost:5001/interactions | grep "Interactions"
```

**Acceptance Criteria:**
- [ ] Glossary page loads without errors
- [ ] All 11 interaction types displayed with definitions
- [ ] All 12 lifecycle stages displayed with details
- [ ] Navigation accessible from all pages
- [ ] No console errors in browser
- [ ] Page is responsive on mobile
- [ ] All existing pages still functional

**Sign-off:** _________________ Date: _________

---

## Feature 1.2: Inline Tooltips and Help

**Priority**: HIGH
**Estimated Time**: 3-4 hours
**Dependencies**: Feature 1.1 (glossary must exist for links)
**Backward Compatibility**: 100% - Enhanced UX, no breaking changes

### Implementation Steps

#### Step 1.2.1: Enable Bootstrap Tooltips Globally

**File**: `templates/streamlined_base.html`
**Action**: Add tooltip initialization script before `</body>` tag

```html
<!-- Add before closing </body> tag -->
<script>
// Initialize Bootstrap tooltips globally
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
</script>
```

**Preservation Check:**
- ✅ Uses Bootstrap 5 (already loaded in base template)
- ✅ DOMContentLoaded ensures no conflict with existing scripts
- ✅ Purely additive - doesn't affect pages without tooltips

#### Step 1.2.2: Add Tooltips to Add Interaction Form

**File**: `templates/streamlined_add_interaction.html`
**Action**: Enhance form labels with help icons and tooltips

**Current state check:**
```bash
grep -n "Interaction Type" templates/streamlined_add_interaction.html
```

**Replace existing form labels** (around lines 36-52):

```html
<!-- BEFORE (around line 36): -->
<label for="interaction_type" class="form-label">Interaction Type</label>

<!-- AFTER: -->
<label for="interaction_type" class="form-label">
    Interaction Type
    <a href="{{ url_for('glossary') }}#interaction-types" target="_blank"
       class="text-muted ms-1"
       data-bs-toggle="tooltip"
       data-bs-placement="top"
       title="View detailed definitions and examples in the glossary">
        <i class="fas fa-question-circle"></i>
    </a>
</label>
```

**Apply to all major fields:**

1. **Source Tool** (line ~16):
```html
<label for="source_tool_id" class="form-label">
    Source Tool
    <span class="text-muted ms-1"
          data-bs-toggle="tooltip"
          data-bs-placement="top"
          title="The tool that initiates or provides data/functionality in this interaction">
        <i class="fas fa-question-circle"></i>
    </span>
</label>
```

2. **Target Tool** (line ~25):
```html
<label for="target_tool_id" class="form-label">
    Target Tool
    <span class="text-muted ms-1"
          data-bs-toggle="tooltip"
          data-bs-placement="top"
          title="The tool that receives data/functionality in this interaction">
        <i class="fas fa-question-circle"></i>
    </span>
</label>
```

3. **Lifecycle Stage** (line ~45):
```html
<label for="lifecycle_stage" class="form-label">
    Lifecycle Stage
    <a href="{{ url_for('glossary') }}#lifecycle-stages" target="_blank"
       class="text-muted ms-1"
       data-bs-toggle="tooltip"
       data-bs-placement="top"
       title="Which research data lifecycle stage does this interaction primarily support?">
        <i class="fas fa-question-circle"></i>
    </a>
</label>
```

4. **Description** (line ~54):
```html
<label for="description" class="form-label">
    Description
    <span class="text-muted ms-1"
          data-bs-toggle="tooltip"
          data-bs-placement="top"
          title="Describe what happens in this interaction and why it's useful (1-3 sentences)">
        <i class="fas fa-question-circle"></i>
    </span>
</label>
```

5. **Technical Details** (line ~62):
```html
<label for="technical_details" class="form-label">
    Technical Implementation
    <span class="text-muted ms-1"
          data-bs-toggle="tooltip"
          data-bs-placement="top"
          title="Mention protocols, APIs, standards, or technologies used (e.g., REST API, OAuth 2.0)">
        <i class="fas fa-question-circle"></i>
    </span>
</label>
```

6. **Benefits** (line ~66):
```html
<label for="benefits" class="form-label">
    Benefits
    <span class="text-muted ms-1"
          data-bs-toggle="tooltip"
          data-bs-placement="top"
          title="What advantages does this interaction provide?">
        <i class="fas fa-question-circle"></i>
    </span>
</label>
```

7. **Challenges** (line ~70):
```html
<label for="challenges" class="form-label">
    Challenges
    <span class="text-muted ms-1"
          data-bs-toggle="tooltip"
          data-bs-placement="top"
          title="What limitations, difficulties, or trade-offs exist?">
        <i class="fas fa-question-circle"></i>
    </span>
</label>
```

**Preservation Check:**
- ✅ Existing labels preserved, only enhanced with help icons
- ✅ Form structure unchanged
- ✅ All required/optional attributes maintained
- ✅ No JavaScript required beyond Bootstrap (already loaded)

#### Step 1.2.3: Add Contextual Help Text

**File**: `templates/streamlined_add_interaction.html`
**Action**: Add `<div class="form-text">` helpers below key fields

**Add below description field** (after line ~57):
```html
<textarea class="form-control" id="description" name="description" rows="3"
          placeholder="Describe the interaction in detail." required></textarea>
<div class="form-text">
    <small class="text-muted">
        <i class="fas fa-info-circle me-1"></i>
        Explain what the interaction does and why it's useful. See
        <a href="{{ url_for('glossary') }}#contributing" target="_blank">contributing guide</a>
        for examples.
    </small>
</div>
```

**Add below technical details field** (after line ~64):
```html
<textarea class="form-control" id="technical_details" name="technical_details" rows="2"
          placeholder="e.g., REST API, OAuth 2.0"></textarea>
<div class="form-text">
    <small class="text-muted">Optional but recommended. Include APIs, protocols, or standards used.</small>
</div>
```

**Preservation Check:**
- ✅ Uses Bootstrap's `.form-text` class (existing pattern)
- ✅ Additive - doesn't modify existing form elements
- ✅ Provides guidance without being intrusive

#### Step 1.2.4: Dynamic Interaction Type Help

**File**: `templates/streamlined_add_interaction.html`
**Action**: Add JavaScript to show example when interaction type selected

**Add before closing `{% endblock %}` tag** (around line 180):

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    const interactionTypeSelect = document.getElementById('interaction_type');

    // Create help text container if it doesn't exist
    let helpContainer = document.getElementById('interaction-type-help');
    if (!helpContainer) {
        helpContainer = document.createElement('div');
        helpContainer.id = 'interaction-type-help';
        helpContainer.className = 'form-text mt-2';
        interactionTypeSelect.parentElement.appendChild(helpContainer);
    }

    // Interaction type examples (from glossary definitions)
    const interactionExamples = {
        'API Integration': 'Example: DMPTool connects to RSpace via REST API to sync data management plans',
        'Data Exchange': 'Example: Zenodo receives data files exported from GitHub repositories',
        'Metadata Exchange': 'Example: ORCID profile information linked to publications in Zenodo',
        'File Format Conversion': 'Example: Converting CSV data to Parquet format for analysis',
        'Workflow Integration': 'Example: Jupyter Notebook packaged with Docker for reproducible analysis',
        'Plugin/Extension': 'Example: Zotero plugin installed in Microsoft Word for citation management',
        'Direct Database Connection': 'Example: Analysis tool connects directly to PostgreSQL research database',
        'Web Service': 'Example: Data repository accessed via OAI-PMH harvesting protocol',
        'Command Line Interface': 'Example: Python script calls FFmpeg via command line to process video data',
        'Import/Export': 'Example: Export CSV from REDCap, import into R for analysis',
        'Other': 'Please describe your interaction type in the Technical Details field'
    };

    // Update help text when selection changes
    interactionTypeSelect.addEventListener('change', function() {
        const selectedType = this.value;
        if (selectedType && interactionExamples[selectedType]) {
            helpContainer.innerHTML = `
                <small class="text-info">
                    <i class="fas fa-lightbulb me-1"></i>
                    ${interactionExamples[selectedType]}
                </small>
            `;
            helpContainer.style.display = 'block';
        } else {
            helpContainer.style.display = 'none';
        }
    });

    // Show help for pre-selected value (edit form)
    if (interactionTypeSelect.value) {
        interactionTypeSelect.dispatchEvent(new Event('change'));
    }
});
</script>
```

**Preservation Check:**
- ✅ Checks for existing elements before creating
- ✅ Works on both add and edit forms
- ✅ Non-blocking - form works even if script fails
- ✅ No external dependencies

### 🔴 HUMAN REVIEW CHECKPOINT 3: Feature 1.2 Complete
**Reviewer Actions:**
- [ ] Test tooltips appear on hover
- [ ] Verify glossary links open in new tab and link to correct section
- [ ] Check dynamic help appears when interaction type selected
- [ ] Test form submission still works correctly
- [ ] Validate tooltips don't interfere with mobile touch
- [ ] Confirm help text is helpful and accurate
- [ ] Verify no console errors

**Testing Commands:**
```bash
# Start application
python streamlined_app.py

# Navigate to add interaction form
# http://localhost:5001/add-interaction

# Test each tooltip by hovering
# Test interaction type dropdown change event
# Submit a test interaction to verify form still works
```

**Acceptance Criteria:**
- [ ] All help icons display correctly
- [ ] Tooltips appear on hover (desktop) and tap (mobile)
- [ ] Glossary links navigate to correct sections
- [ ] Dynamic help updates when interaction type changes
- [ ] Form submission successful with help elements present
- [ ] No impact on form validation
- [ ] Mobile-friendly (tooltips don't obscure fields)

**Sign-off:** _________________ Date: _________

---

## Feature 1.3: Tool Search/Autocomplete

**Priority**: CRITICAL
**Estimated Time**: 2-3 hours
**Dependencies**: None
**Backward Compatibility**: 100% - Enhanced existing dropdowns
**External Library**: Select2 v4.1.0 (MIT License, CDN-hosted)

### Implementation Steps

#### Step 1.3.1: Add Select2 Library to Base Template

**File**: `templates/streamlined_base.html`
**Action**: Add Select2 CSS and JS in `<head>` section

**Locate the `<head>` section** (typically lines 1-15):

```html
<!-- Add after existing CSS links, before closing </head> -->
<!-- Select2 for enhanced dropdowns -->
<link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
<link href="https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/select2-bootstrap-5-theme.min.css" rel="stylesheet" />
```

**Add before closing `</body>` tag** (after jQuery if present, before custom scripts):

```html
<!-- Select2 JavaScript (requires jQuery) -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
```

**Preservation Check:**
- ✅ CDN-hosted - no local file changes
- ✅ Loaded globally but only affects elements explicitly initialized
- ✅ Bootstrap 5 theme maintains consistent styling
- ✅ jQuery added (required for Select2, won't conflict if already present)

#### Step 1.3.2: Initialize Select2 on Tool Dropdowns

**File**: `templates/streamlined_add_interaction.html`
**Action**: Add Select2 initialization for source and target tool selects

**Add before closing `{% endblock %}` tag** (after existing scripts, around line 179):

```html
<script>
$(document).ready(function() {
    // Initialize Select2 on source tool dropdown
    $('#source_tool_id').select2({
        theme: 'bootstrap-5',
        placeholder: 'Search for a source tool...',
        allowClear: true,
        width: '100%',
        templateResult: formatToolOption,
        templateSelection: formatToolSelection
    });

    // Initialize Select2 on target tool dropdown
    $('#target_tool_id').select2({
        theme: 'bootstrap-5',
        placeholder: 'Search for a target tool...',
        allowClear: true,
        width: '100%',
        templateResult: formatToolOption,
        templateSelection: formatToolSelection
    });

    // Custom formatting for tool options
    function formatToolOption(tool) {
        if (!tool.id) {
            return tool.text;
        }

        // Extract stage info from data attribute
        var $tool = $(tool.element);
        var stage = $tool.data('stage') || '';

        // Build formatted option with icon and stage
        var $result = $(
            '<span>' +
                '<i class="fas fa-tool me-2 text-muted"></i>' +
                '<strong>' + tool.text + '</strong>' +
                (stage ? '<br><small class="text-muted ms-4">Stage: ' + stage + '</small>' : '') +
            '</span>'
        );
        return $result;
    }

    function formatToolSelection(tool) {
        return tool.text;
    }

    // Preserve existing lifecycle stage auto-selection functionality
    const sourceToolSelect = document.getElementById('source_tool_id');
    const targetToolSelect = document.getElementById('target_tool_id');
    const lifecycleStageSelect = document.getElementById('lifecycle_stage');

    function updateLifecycleStage() {
        const sourceOption = sourceToolSelect.options[sourceToolSelect.selectedIndex];
        const targetOption = targetToolSelect.options[targetToolSelect.selectedIndex];

        if (sourceOption && sourceOption.dataset.stage && targetOption && targetOption.dataset.stage) {
            const sourceStage = sourceOption.dataset.stage;
            const targetStage = targetOption.dataset.stage;

            // If both tools are from the same stage, select that stage
            if (sourceStage === targetStage) {
                lifecycleStageSelect.value = sourceStage;
            } else {
                // If tools are from different stages, prioritize the source tool's stage
                lifecycleStageSelect.value = sourceStage;
            }
        } else if (sourceOption && sourceOption.dataset.stage) {
            // If only source tool is selected, use its stage
            lifecycleStageSelect.value = sourceOption.dataset.stage;
        } else if (targetOption && targetOption.dataset.stage) {
            // If only target tool is selected, use its stage
            lifecycleStageSelect.value = targetOption.dataset.stage;
        }
    }

    // Listen for Select2 change events (not native change events)
    $('#source_tool_id').on('select2:select', updateLifecycleStage);
    $('#target_tool_id').on('select2:select', updateLifecycleStage);
});
</script>
```

**Preservation Check:**
- ✅ Preserves existing lifecycle stage auto-selection logic
- ✅ Maintains all data attributes on option elements
- ✅ Works with existing form validation
- ✅ Gracefully degrades if Select2 fails to load

#### Step 1.3.3: Apply Select2 to Edit Interaction Form

**File**: `templates/streamlined_edit_interaction.html`
**Action**: Add same Select2 initialization

**Check if file exists and has tool dropdowns:**
```bash
grep -n "source_tool_id\|target_tool_id" templates/streamlined_edit_interaction.html
```

**Add the same script as in Step 1.3.2** before closing `{% endblock %}` tag.

**Preservation Check:**
- ✅ Edit form maintains existing selected values
- ✅ Pre-selected tools display correctly in Select2
- ✅ Form submission unchanged

#### Step 1.3.4: Fallback for No-JavaScript

**File**: `templates/streamlined_add_interaction.html`
**Action**: Add `<noscript>` warning for accessibility

**Add after opening form tag** (around line 11):

```html
<noscript>
    <div class="alert alert-warning">
        <strong>JavaScript Disabled:</strong> For the best experience, please enable JavaScript.
        Tool dropdowns will be basic without enhanced search.
    </div>
</noscript>
```

**Preservation Check:**
- ✅ Form still functions without JavaScript
- ✅ Basic HTML select works as fallback
- ✅ Accessibility maintained

### 🔴 HUMAN REVIEW CHECKPOINT 4: Feature 1.3 Complete
**Reviewer Actions:**
- [ ] Test tool search with partial names
- [ ] Verify dropdown displays stage information
- [ ] Check that lifecycle stage auto-selection still works
- [ ] Test form submission with selected tools
- [ ] Validate edit form shows pre-selected tools correctly
- [ ] Test on browsers: Chrome, Firefox, Safari, Edge
- [ ] Verify fallback works with JavaScript disabled
- [ ] Check mobile touch interaction

**Testing Commands:**
```bash
# Start application
python streamlined_app.py

# Navigate to add interaction form
# Test search: type "Git" - should show GitHub, GitLab, etc.
# Test selection - verify lifecycle stage updates
# Submit form - verify tools saved correctly

# Navigate to edit interaction
# Verify pre-selected tools appear in Select2 dropdown
```

**Acceptance Criteria:**
- [ ] Search filters tools as user types
- [ ] Tools display with stage information
- [ ] Selecting tool updates lifecycle stage (existing behavior preserved)
- [ ] Form submission works correctly
- [ ] Edit form shows pre-selected tools
- [ ] Dropdown styling matches Bootstrap theme
- [ ] Performance acceptable with 267 tools
- [ ] Mobile-friendly on tablets and phones

**Sign-off:** _________________ Date: _________

---

## Feature 1.4: CSV Template Download

**Priority**: HIGH
**Estimated Time**: 2 hours
**Dependencies**: None
**Backward Compatibility**: 100% - New feature, no changes to existing functionality

### Implementation Steps

#### Step 1.4.1: Create CSV Template Route

**File**: `streamlined_app.py`
**Action**: Add new route after existing CSV export route (around line 430)

**Locate the existing CSV export route:**
```bash
grep -n "@app.route('/export/interactions/csv')" streamlined_app.py
```

**Add new route after it** (typically around line 450):

```python
@app.route('/download/csv-template')
def download_csv_template():
    """
    Provide a CSV template with example data to help users prepare bulk uploads.

    This template includes:
    - Proper column headers matching database schema
    - Two example rows demonstrating good data quality
    - Different interaction types and lifecycle stages for reference

    Returns:
        CSV file download response
    """
    try:
        # Define template data with high-quality examples
        template_data = [
            {
                'Source Tool': 'GitHub',
                'Target Tool': 'Zenodo',
                'Interaction Type': 'Data Exchange',
                'Lifecycle Stage': 'PRESERVE',
                'Description': 'GitHub repositories can be automatically archived to Zenodo with DOI assignment, creating permanent records of research software and datasets.',
                'Technical Details': 'GitHub webhook integration, automatic metadata transfer via Zenodo API',
                'Benefits': 'Permanent preservation, citable software versions with DOIs, enhanced reproducibility',
                'Challenges': 'Large repository size limits, selective file archiving complexity, metadata mapping',
                'Examples': 'Software packages automatically archived with each GitHub release; Research code preserved with version-specific DOIs',
                'Contact Person': 'Your Name',
                'Organization': 'Your Institution',
                'Email': 'your.email@example.com',
                'Priority': 'medium',
                'Complexity': 'simple',
                'Status': 'implemented',
                'Submitted By': 'Template Example'
            },
            {
                'Source Tool': 'REDCap',
                'Target Tool': 'R',
                'Interaction Type': 'API Integration',
                'Lifecycle Stage': 'ANALYSE',
                'Description': 'REDCap provides direct export capabilities to R for statistical analysis, streamlining the transition from data collection to analysis workflows.',
                'Technical Details': 'REDCap API with R packages (REDCapR, redcapAPI), OAuth authentication, automated data synchronization',
                'Benefits': 'Seamless data workflow, reduced manual errors, reproducible analysis pipelines, real-time data access',
                'Challenges': 'Data format conversion complexity, access control management, API rate limits, authentication setup',
                'Examples': 'Clinical trial data exported from REDCap for statistical analysis in R; Longitudinal study data automatically synced for ongoing analysis',
                'Contact Person': '',
                'Organization': '',
                'Email': '',
                'Priority': 'high',
                'Complexity': 'moderate',
                'Status': 'implemented',
                'Submitted By': 'Template Example'
            },
            {
                'Source Tool': 'Jupyter Notebook',
                'Target Tool': 'Docker',
                'Interaction Type': 'Workflow Integration',
                'Lifecycle Stage': 'ANALYSE',
                'Description': 'Jupyter notebooks can be containerized using Docker to ensure reproducible computational environments across different systems and platforms.',
                'Technical Details': 'Docker containerization, Jupyter Docker stacks, environment specification via Dockerfile',
                'Benefits': 'Reproducible environments, easy deployment, consistent dependencies across systems, version-controlled infrastructure',
                'Challenges': 'Container size optimization, security considerations, learning curve for container technology',
                'Examples': 'Data analysis notebooks packaged as Docker containers for reproducible research; Machine learning workflows containerized for deployment',
                'Contact Person': '',
                'Organization': '',
                'Email': '',
                'Priority': 'medium',
                'Complexity': 'complex',
                'Status': 'implemented',
                'Submitted By': 'Template Example'
            }
        ]

        # Create CSV in memory
        output = StringIO()

        # Define fieldnames matching database schema
        fieldnames = [
            'Source Tool', 'Target Tool', 'Interaction Type', 'Lifecycle Stage',
            'Description', 'Technical Details', 'Benefits', 'Challenges', 'Examples',
            'Contact Person', 'Organization', 'Email', 'Priority', 'Complexity',
            'Status', 'Submitted By'
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(template_data)

        # Prepare response
        csv_content = output.getvalue()
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=prism_interaction_template.csv'

        logger.info("CSV template downloaded successfully")
        return response

    except Exception as e:
        logger.error(f"Error generating CSV template: {e}")
        flash('Error generating CSV template. Please try again.', 'error')
        return redirect(url_for('index'))
```

**Preservation Check:**
- ✅ New route, doesn't modify existing CSV export
- ✅ Uses existing imports (csv, StringIO, make_response)
- ✅ No database access - generates template data
- ✅ Error handling follows existing pattern

#### Step 1.4.2: Add Download Link to CSV Upload Page

**File**: `templates/streamlined_upload_csv.html`
**Action**: Add prominent template download button

**Locate the upload form** (check if file exists):
```bash
ls -la templates/streamlined_upload_csv.html
```

**Add before the upload form** (typically near the top of content area):

```html
<!-- Add after page title, before upload form -->
<div class="alert alert-info border-0 mb-4">
    <div class="row align-items-center">
        <div class="col-md-8">
            <h5 class="alert-heading mb-2">
                <i class="fas fa-download me-2"></i>Need a Template?
            </h5>
            <p class="mb-0">
                Download our CSV template with example interactions to get started.
                The template includes proper column headers and three complete examples
                demonstrating different interaction types.
            </p>
        </div>
        <div class="col-md-4 text-center">
            <a href="{{ url_for('download_csv_template') }}"
               class="btn btn-primary btn-lg">
                <i class="fas fa-file-csv me-2"></i>Download Template
            </a>
        </div>
    </div>
</div>
```

**Preservation Check:**
- ✅ Additive - doesn't modify existing upload form
- ✅ Uses existing alert styling
- ✅ Responsive design with Bootstrap grid

#### Step 1.4.3: Add Template Link to Navigation

**File**: `templates/streamlined_base.html`
**Action**: Add template download to CSV submenu (if exists) or as separate link

**Find CSV-related navigation** (if it exists):
```bash
grep -n "CSV\|csv" templates/streamlined_base.html
```

**Option A: If dropdown menu exists, add to it:**
```html
<li>
    <a class="dropdown-item" href="{{ url_for('download_csv_template') }}">
        <i class="fas fa-file-csv me-2"></i>Download CSV Template
    </a>
</li>
```

**Option B: If no CSV menu, add as standalone link:**
```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('download_csv_template') }}"
       data-bs-toggle="tooltip"
       title="Download CSV template for bulk uploads">
        <i class="fas fa-file-csv me-1"></i>CSV Template
    </a>
</li>
```

**Preservation Check:**
- ✅ Follows existing navigation pattern
- ✅ Doesn't modify existing links
- ✅ Accessible from all pages

#### Step 1.4.4: Update Glossary Contributing Section

**File**: `templates/glossary.html`
**Action**: Add template download link to CSV contributing guide

**Locate the contributing section** (created in Feature 1.1, around line 400):

```html
<!-- Update the CSV upload section -->
<div class="card border-0 shadow-sm">
    <div class="card-body">
        <h5>Bulk Upload via CSV</h5>
        <p>For adding multiple interactions:</p>
        <ol>
            <li>
                Download the
                <a href="{{ url_for('download_csv_template') }}">
                    <i class="fas fa-file-csv me-1"></i>CSV template
                </a>
                with example interactions
            </li>
            <li>Prepare your data following the same structure and format</li>
            <li>Ensure tool names match existing tools in PRISM (or new tools will be created)</li>
            <li>Review the interaction type and lifecycle stage definitions above</li>
            <li>Use the <a href="{{ url_for('upload_csv') }}">CSV upload page</a> to submit your file</li>
            <li>Review the results and fix any errors reported</li>
        </ol>

        <div class="alert alert-success border-0 mt-3 mb-0">
            <h6 class="alert-heading">
                <i class="fas fa-check-circle me-2"></i>Template Benefits
            </h6>
            <ul class="mb-0">
                <li>Correct column headers and order</li>
                <li>Example interactions demonstrating data quality</li>
                <li>All required and optional fields shown</li>
                <li>Valid values for Priority, Complexity, and Status</li>
            </ul>
        </div>
    </div>
</div>
```

**Preservation Check:**
- ✅ Enhances existing contributing guide
- ✅ Maintains existing CSV upload instructions
- ✅ Provides additional guidance

### 🔴 HUMAN REVIEW CHECKPOINT 5: Feature 1.4 Complete
**Reviewer Actions:**
- [ ] Download CSV template and verify contents
- [ ] Check template has correct column headers
- [ ] Verify example data is accurate and helpful
- [ ] Test uploading the downloaded template (should work as-is)
- [ ] Check template link appears on upload page
- [ ] Verify navigation link works
- [ ] Validate file downloads with correct filename
- [ ] Review example interactions for quality and accuracy

**Testing Commands:**
```bash
# Start application
python streamlined_app.py

# Test template download
curl -o template.csv http://localhost:5001/download/csv-template

# Verify CSV contents
cat template.csv

# Check CSV can be uploaded
# Navigate to upload page and upload template.csv
```

**Acceptance Criteria:**
- [ ] Template downloads successfully
- [ ] Filename is "prism_interaction_template.csv"
- [ ] CSV has proper headers
- [ ] Template includes 3 example rows
- [ ] Examples demonstrate different interaction types
- [ ] Examples show both required and optional fields
- [ ] Upload page prominently displays download button
- [ ] Template can be uploaded without modifications
- [ ] Example data creates valid interactions

**Sign-off:** _________________ Date: _________

---

## Feature 1.5: Basic Search Functionality

**Priority**: HIGH
**Estimated Time**: 2-3 hours
**Dependencies**: None
**Backward Compatibility**: 100% - Enhancement to existing view

### Implementation Steps

#### Step 1.5.1: Add Search UI to Interactions View

**File**: `templates/streamlined_view_interactions.html`
**Action**: Add search and filter controls before the interactions table

**Locate the table** (around line 10):
```bash
grep -n "<table" templates/streamlined_view_interactions.html
```

**Add before the `<table>` element** (around line 9-10):

```html
<!-- Search and Filter Controls -->
<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-light">
        <h5 class="mb-0">
            <i class="fas fa-filter me-2"></i>Search & Filter Interactions
        </h5>
    </div>
    <div class="card-body">
        <div class="row g-3">
            <!-- Text Search -->
            <div class="col-md-4">
                <label for="search-input" class="form-label">
                    Search
                    <span class="text-muted ms-1"
                          data-bs-toggle="tooltip"
                          title="Search tool names, descriptions, and technical details">
                        <i class="fas fa-question-circle"></i>
                    </span>
                </label>
                <input type="text" class="form-control" id="search-input"
                       placeholder="Search by tool name, description...">
            </div>

            <!-- Interaction Type Filter -->
            <div class="col-md-3">
                <label for="filter-type" class="form-label">Interaction Type</label>
                <select class="form-select" id="filter-type">
                    <option value="">All Types</option>
                    {% for interaction_type in interaction_types %}
                    <option value="{{ interaction_type }}">{{ interaction_type }}</option>
                    {% endfor %}
                </select>
            </div>

            <!-- Lifecycle Stage Filter -->
            <div class="col-md-3">
                <label for="filter-stage" class="form-label">Lifecycle Stage</label>
                <select class="form-select" id="filter-stage">
                    <option value="">All Stages</option>
                    {% for stage in stages %}
                    <option value="{{ stage.name }}">{{ stage.name }}</option>
                    {% endfor %}
                </select>
            </div>

            <!-- Clear Button -->
            <div class="col-md-2 d-flex align-items-end">
                <button class="btn btn-outline-secondary w-100" id="clear-filters">
                    <i class="fas fa-times me-1"></i>Clear Filters
                </button>
            </div>
        </div>

        <!-- Results Count -->
        <div class="mt-3">
            <div class="alert alert-info border-0 mb-0 py-2" id="result-count-alert">
                <small id="result-count">Loading interactions...</small>
            </div>
        </div>
    </div>
</div>
```

**Preservation Check:**
- ✅ Added before table, doesn't modify existing table structure
- ✅ Uses existing variables (interaction_types, stages)
- ✅ Bootstrap styling maintains consistency
- ✅ Responsive grid layout

#### Step 1.5.2: Update Route to Pass Filter Data

**File**: `streamlined_app.py`
**Action**: Modify view_interactions route to pass filter data

**Locate the view_interactions route** (around line 303):
```bash
grep -n "def view_interactions" streamlined_app.py
```

**Update the route** (around line 303-311):

```python
@app.route('/interactions')
def view_interactions():
    """View all interactions with search and filter support."""
    try:
        interactions = ToolInteraction.query.order_by(ToolInteraction.submitted_at.desc()).all()
        stages = MaldrethStage.query.order_by(MaldrethStage.position).all()

        return render_template('streamlined_view_interactions.html',
                             interactions=interactions,
                             interaction_types=INTERACTION_TYPES,
                             stages=stages)
    except Exception as e:
        logger.error(f"Error viewing interactions: {e}")
        return render_template('error.html', error=str(e)), 500
```

**Preservation Check:**
- ✅ Maintains existing query logic
- ✅ Adds new template variables without breaking existing ones
- ✅ Error handling unchanged

#### Step 1.5.3: Implement Client-Side Filter Logic

**File**: `templates/streamlined_view_interactions.html`
**Action**: Add JavaScript for filtering

**Add before closing `{% endblock %}` tag** (around line 75):

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Get all filter elements
    const searchInput = document.getElementById('search-input');
    const filterType = document.getElementById('filter-type');
    const filterStage = document.getElementById('filter-stage');
    const clearButton = document.getElementById('clear-filters');
    const resultCountElement = document.getElementById('result-count');

    // Get all table rows (excluding header)
    const tableRows = document.querySelectorAll('tbody tr');
    const totalRows = tableRows.length;

    /**
     * Main filter function - applies all active filters
     */
    function filterTable() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const selectedType = filterType.value.toLowerCase();
        const selectedStage = filterStage.value.toLowerCase();

        let visibleCount = 0;

        tableRows.forEach(row => {
            // Get row text content for searching
            const rowText = row.textContent.toLowerCase();

            // Apply search filter
            const matchesSearch = !searchTerm || rowText.includes(searchTerm);

            // Apply interaction type filter
            const matchesType = !selectedType || rowText.includes(selectedType);

            // Apply lifecycle stage filter
            const matchesStage = !selectedStage || rowText.includes(selectedStage);

            // Show row only if all filters match
            if (matchesSearch && matchesType && matchesStage) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Update result count
        updateResultCount(visibleCount, totalRows);
    }

    /**
     * Update the result count display
     */
    function updateResultCount(visible, total) {
        if (visible === total) {
            resultCountElement.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                Showing all <strong>${total}</strong> interaction(s)
            `;
            document.getElementById('result-count-alert').className = 'alert alert-info border-0 mb-0 py-2';
        } else {
            resultCountElement.innerHTML = `
                <i class="fas fa-filter me-2"></i>
                Showing <strong>${visible}</strong> of <strong>${total}</strong> interaction(s)
            `;
            document.getElementById('result-count-alert').className = 'alert alert-success border-0 mb-0 py-2';
        }
    }

    /**
     * Clear all filters and show all rows
     */
    function clearFilters() {
        searchInput.value = '';
        filterType.value = '';
        filterStage.value = '';
        filterTable();
    }

    // Event listeners
    searchInput.addEventListener('keyup', filterTable);
    searchInput.addEventListener('search', filterTable); // For search input clear button
    filterType.addEventListener('change', filterTable);
    filterStage.addEventListener('change', filterTable);
    clearButton.addEventListener('click', clearFilters);

    // Initialize count on page load
    updateResultCount(totalRows, totalRows);

    // Persist filters across page navigation (optional enhancement)
    // Save filter state to sessionStorage
    function saveFilterState() {
        sessionStorage.setItem('prism_search', searchInput.value);
        sessionStorage.setItem('prism_filter_type', filterType.value);
        sessionStorage.setItem('prism_filter_stage', filterStage.value);
    }

    // Restore filter state on page load
    function restoreFilterState() {
        const savedSearch = sessionStorage.getItem('prism_search');
        const savedType = sessionStorage.getItem('prism_filter_type');
        const savedStage = sessionStorage.getItem('prism_filter_stage');

        if (savedSearch) searchInput.value = savedSearch;
        if (savedType) filterType.value = savedType;
        if (savedStage) filterStage.value = savedStage;

        // Apply restored filters
        if (savedSearch || savedType || savedStage) {
            filterTable();
        }
    }

    // Restore previous filters
    restoreFilterState();

    // Save filters when they change
    searchInput.addEventListener('change', saveFilterState);
    filterType.addEventListener('change', saveFilterState);
    filterStage.addEventListener('change', saveFilterState);

    // Clear saved state when clearing filters
    clearButton.addEventListener('click', function() {
        sessionStorage.removeItem('prism_search');
        sessionStorage.removeItem('prism_filter_type');
        sessionStorage.removeItem('prism_filter_stage');
    });
});
</script>
```

**Preservation Check:**
- ✅ Client-side only - no server changes required
- ✅ Works with existing table structure
- ✅ No external dependencies
- ✅ Progressive enhancement - table works without JavaScript

#### Step 1.5.4: Add "No Results" Message

**File**: `templates/streamlined_view_interactions.html`
**Action**: Add row to display when filters return no results

**Add after the table's `{% endfor %}` loop** (inside `<tbody>`, around line 63):

```html
{% endfor %}
<!-- No results message (hidden by default, shown by JavaScript) -->
<tr id="no-results-row" style="display: none;">
    <td colspan="7" class="text-center py-5">
        <i class="fas fa-search fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">No interactions match your filters</h5>
        <p class="text-muted">Try adjusting your search terms or filters</p>
        <button class="btn btn-outline-primary" onclick="document.getElementById('clear-filters').click()">
            <i class="fas fa-times me-2"></i>Clear Filters
        </button>
    </td>
</tr>
```

**Update the filterTable function** to show/hide no results row:

```javascript
// In the filterTable function, after the forEach loop:
function filterTable() {
    // ... existing code ...

    // Show/hide no results message
    const noResultsRow = document.getElementById('no-results-row');
    if (visibleCount === 0) {
        noResultsRow.style.display = '';
    } else {
        noResultsRow.style.display = 'none';
    }

    // Update result count
    updateResultCount(visibleCount, totalRows);
}
```

**Preservation Check:**
- ✅ Hidden by default - doesn't show when JavaScript disabled
- ✅ Uses existing table structure
- ✅ Provides clear user feedback

### 🔴 HUMAN REVIEW CHECKPOINT 6: Feature 1.5 Complete
**Reviewer Actions:**
- [ ] Test search with various terms (tool names, descriptions)
- [ ] Verify filter by interaction type works
- [ ] Check filter by lifecycle stage works
- [ ] Test combining search + filters
- [ ] Validate clear filters button resets everything
- [ ] Check result count updates correctly
- [ ] Verify "no results" message appears appropriately
- [ ] Test filter persistence across page navigation (sessionStorage)
- [ ] Validate table still works without JavaScript

**Testing Commands:**
```bash
# Start application
python streamlined_app.py

# Navigate to interactions view
# http://localhost:5001/interactions

# Test scenarios:
# 1. Search for "GitHub" - should filter results
# 2. Select "API Integration" type - should filter
# 3. Select "PRESERVE" stage - should filter
# 4. Combine all three filters
# 5. Clear filters - should show all
# 6. Search for nonsense - should show "no results"
```

**Acceptance Criteria:**
- [ ] Search filters results as user types
- [ ] Interaction type dropdown filters correctly
- [ ] Lifecycle stage dropdown filters correctly
- [ ] Multiple filters work together (AND logic)
- [ ] Clear button resets all filters
- [ ] Result count displays correctly
- [ ] "No results" message appears when appropriate
- [ ] Filters persist when navigating back to page
- [ ] Performance acceptable with large datasets
- [ ] Mobile-friendly interface

**Sign-off:** _________________ Date: _________

---

## Testing Protocol

### Pre-Deployment Testing

#### 1. Unit Testing

**Create test file**: `tests/test_phase1_features.py` (if tests directory doesn't exist, create it)

```python
"""
Unit tests for Phase 1 usability improvements
"""
import pytest
from streamlined_app import app, db

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_glossary_route_exists(client):
    """Test that glossary route is accessible"""
    response = client.get('/glossary')
    assert response.status_code == 200
    assert b'Glossary' in response.data

def test_csv_template_download(client):
    """Test CSV template download"""
    response = client.get('/download/csv-template')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv'
    assert b'Source Tool,Target Tool' in response.data

def test_interactions_view_with_filters(client):
    """Test interactions view includes filter elements"""
    response = client.get('/interactions')
    assert response.status_code == 200
    assert b'search-input' in response.data
    assert b'filter-type' in response.data
    assert b'filter-stage' in response.data

def test_existing_routes_still_work(client):
    """Ensure all existing routes remain functional"""
    routes = [
        '/',
        '/add-interaction',
        '/interactions',
        '/about'
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code in [200, 302], f"Route {route} failed"

# Run with: pytest tests/test_phase1_features.py -v
```

#### 2. Integration Testing

**Manual Testing Checklist**:

- [ ] **Homepage**
  - Glossary link in navigation works
  - CSV template link (if added) works
  - Existing functionality intact

- [ ] **Glossary Page**
  - All 11 interaction types displayed
  - All 12 lifecycle stages displayed
  - Examples are accurate
  - Links to other pages work
  - Mobile responsive

- [ ] **Add Interaction Form**
  - Tooltips appear on hover
  - Help icons link to glossary
  - Select2 tool search works
  - Dynamic help text appears
  - Form validation unchanged
  - Form submission successful
  - Lifecycle stage auto-selection works

- [ ] **Edit Interaction Form**
  - Select2 shows pre-selected tools
  - All enhancements present
  - Form updates work

- [ ] **View Interactions**
  - Search filters results
  - Type filter works
  - Stage filter works
  - Combined filters work
  - Clear filters works
  - Result count accurate
  - No results message appears

- [ ] **CSV Upload**
  - Template download button present
  - Template downloads correctly
  - Template upload works

#### 3. Browser Compatibility Testing

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

#### 4. Performance Testing

```bash
# Test page load times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5001/glossary
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5001/interactions

# curl-format.txt contents:
# time_namelookup:  %{time_namelookup}\n
# time_connect:  %{time_connect}\n
# time_appconnect:  %{time_appconnect}\n
# time_pretransfer:  %{time_pretransfer}\n
# time_redirect:  %{time_redirect}\n
# time_starttransfer:  %{time_starttransfer}\n
# ----------\n
# time_total:  %{time_total}\n
```

**Acceptance**: All pages load in < 2 seconds on local development.

#### 5. Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Screen reader compatibility (test with NVDA/JAWS)
- [ ] Color contrast meets WCAG AA standards
- [ ] Form labels properly associated
- [ ] Alt text for icons where needed
- [ ] Skip navigation links work

### 🔴 HUMAN REVIEW CHECKPOINT 7: Testing Complete
**Reviewer Actions:**
- [ ] Review all test results
- [ ] Verify no regressions in existing functionality
- [ ] Confirm all new features work as specified
- [ ] Check performance metrics acceptable
- [ ] Validate cross-browser compatibility
- [ ] Review accessibility compliance
- [ ] Document any issues found
- [ ] Decide: Ready for deployment or needs fixes?

**Test Summary:**
- Total tests run: _____
- Passed: _____
- Failed: _____
- Issues found: _____

**Sign-off:** _________________ Date: _________

---

## Deployment Checklist

### Pre-Deployment

- [ ] **Code Review**
  - All human review checkpoints signed off
  - Code follows existing style conventions
  - No commented-out code or debug statements
  - All TODOs addressed or documented

- [ ] **Database Backup**
  - Development database backed up
  - Production database backup verified (Heroku)
  - Backup restore tested

- [ ] **Version Control**
  - All changes committed to feature branch
  - Commit messages are descriptive
  - No secrets in repository
  - .gitignore updated if needed

- [ ] **Documentation**
  - CHANGELOG.md updated
  - README.md updated if needed
  - This implementation plan marked complete

- [ ] **Dependencies**
  - No new Python dependencies (all CDN-based)
  - requirements.txt unchanged
  - External CDNs accessible and reliable

### Deployment Steps

#### Option A: Development/Staging Deployment

```bash
# 1. Merge feature branch to main
git checkout main
git merge phase-1-usability-improvements

# 2. Restart application
# (Development)
python streamlined_app.py

# 3. Smoke test
curl http://localhost:5001/ | grep "PRISM"
curl http://localhost:5001/glossary | grep "Glossary"
curl http://localhost:5001/interactions | grep "search-input"
```

#### Option B: Production Deployment (Heroku)

```bash
# 1. Verify production backup
heroku pg:backups:capture --app mal2-data-survey-cb27f6674f20

# 2. Push to production
git push heroku main

# 3. Monitor deployment
heroku logs --tail --app mal2-data-survey-cb27f6674f20

# 4. Smoke test production
curl https://mal2-data-survey-cb27f6674f20.herokuapp.com/ | grep "PRISM"
curl https://mal2-data-survey-cb27f6674f20.herokuapp.com/glossary | grep "Glossary"

# 5. Test in browser
# Navigate to each new feature and verify
```

### Post-Deployment

- [ ] **Verification**
  - All new routes accessible
  - Existing functionality works
  - No errors in application logs
  - Database intact and accessible

- [ ] **Monitoring**
  - Check error logs for 24 hours
  - Monitor user feedback
  - Track analytics for new pages
  - Note any performance issues

- [ ] **Communication**
  - Announce new features to MaLDReTH II group
  - Update user documentation
  - Share glossary link in communications
  - Collect initial user feedback

### 🔴 HUMAN REVIEW CHECKPOINT 8: Deployment Complete
**Reviewer Actions:**
- [ ] Verify production deployment successful
- [ ] Test all features in production environment
- [ ] Check application logs for errors
- [ ] Confirm database integrity
- [ ] Validate external CDN resources loading
- [ ] Test from different networks/locations
- [ ] Announce deployment to stakeholders

**Production URLs Tested:**
- [ ] Homepage: https://mal2-data-survey-cb27f6674f20.herokuapp.com/
- [ ] Glossary: https://mal2-data-survey-cb27f6674f20.herokuapp.com/glossary
- [ ] Add Interaction: https://mal2-data-survey-cb27f6674f20.herokuapp.com/add-interaction
- [ ] View Interactions: https://mal2-data-survey-cb27f6674f20.herokuapp.com/interactions
- [ ] CSV Template: https://mal2-data-survey-cb27f6674f20.herokuapp.com/download/csv-template

**Sign-off:** _________________ Date: _________

---

## Rollback Plan

### If Issues Detected Post-Deployment

#### Level 1: Minor Issues (Non-Breaking)
**Examples**: Typos, styling glitches, minor UX issues

**Action**: Fix in place
```bash
# Make fixes on main branch
git add <fixed-files>
git commit -m "fix: address minor issues in Phase 1 features"
git push heroku main
```

#### Level 2: Feature-Specific Issues
**Examples**: Select2 not loading, tooltips not working, CSV template errors

**Action**: Disable specific feature
```bash
# Option 1: Comment out problematic code
# Option 2: Add feature flag

# In streamlined_app.py
ENABLE_SELECT2 = False  # Set to False to disable Select2

# In templates
{% if config.get('ENABLE_SELECT2', True) %}
    <!-- Select2 code -->
{% endif %}
```

#### Level 3: Critical Issues (Breaking)
**Examples**: Routes broken, database errors, application won't start

**Action**: Full rollback

```bash
# 1. Revert to previous commit
git log --oneline -10  # Find last good commit
git revert <commit-hash>
git push heroku main

# 2. Restore database if needed
heroku pg:backups:restore <backup-id> --app mal2-data-survey-cb27f6674f20

# 3. Verify rollback successful
curl https://mal2-data-survey-cb27f6674f20.herokuapp.com/ | grep "PRISM"

# 4. Notify stakeholders
# 5. Investigate issues in development
# 6. Re-implement with fixes
```

### Rollback Decision Matrix

| Issue Severity | User Impact | Rollback Action | Timeframe |
|----------------|-------------|-----------------|-----------|
| Low | <10% affected, workaround exists | Fix in place | 24-48 hours |
| Medium | 10-50% affected, degraded experience | Disable feature | 4-8 hours |
| High | >50% affected, critical path broken | Partial rollback | 1-2 hours |
| Critical | Site down or data at risk | Full rollback | Immediate |

### 🔴 HUMAN REVIEW CHECKPOINT 9: Rollback Decision
**If rollback required:**

**Issue Description**: _________________________________

**Severity Level**: [ ] Low [ ] Medium [ ] High [ ] Critical

**Rollback Action Taken**: _________________________________

**Estimated Fix Time**: _________________________________

**User Communication**: _________________________________

**Sign-off:** _________________ Date: _________

---

## Success Metrics

### Immediate (Week 1-2)

- [ ] Zero critical bugs in production
- [ ] All 5 features deployed and functional
- [ ] No performance degradation
- [ ] Existing functionality 100% preserved

### Short-term (Week 3-4)

- [ ] Glossary page views > 20% of total traffic
- [ ] CSV template downloads > 10
- [ ] Average time on add interaction form reduced by 20%
- [ ] Search feature used in >50% of interaction view sessions
- [ ] User feedback positive (if collected)

### Medium-term (Month 2-3)

- [ ] Interaction submission rate increased by 30%
- [ ] Higher quality submissions (more complete fields)
- [ ] Reduced support questions about terminology
- [ ] Tool selection time reduced (measured via analytics if available)

---

## Phase 1 Completion Checklist

- [ ] Feature 1.1: Interaction Type Definitions & Glossary ✅
- [ ] Feature 1.2: Inline Tooltips and Help ✅
- [ ] Feature 1.3: Tool Search/Autocomplete ✅
- [ ] Feature 1.4: CSV Template Download ✅
- [ ] Feature 1.5: Basic Search Functionality ✅

- [ ] All Human Review Checkpoints completed ✅
- [ ] All tests passing ✅
- [ ] Production deployment successful ✅
- [ ] Documentation updated ✅
- [ ] Stakeholders notified ✅

### Final Sign-Off

**Phase 1 Implementation Complete**

**Lead Developer**: _________________ Date: _________

**Technical Reviewer**: _________________ Date: _________

**MaLDReTH II Co-Chair**: _________________ Date: _________

---

## Appendix A: File Modification Summary

| File | Type | Action | Lines Changed |
|------|------|--------|---------------|
| `streamlined_app.py` | Python | Modified | ~150 added |
| `templates/glossary.html` | HTML | Created | ~500 new |
| `templates/streamlined_base.html` | HTML | Modified | ~15 added |
| `templates/streamlined_add_interaction.html` | HTML | Modified | ~100 added |
| `templates/streamlined_edit_interaction.html` | HTML | Modified | ~50 added |
| `templates/streamlined_view_interactions.html` | HTML | Modified | ~150 added |
| `templates/streamlined_upload_csv.html` | HTML | Modified | ~20 added |

**Total**: ~985 lines added, 0 lines removed, 0 breaking changes

---

## Appendix B: External Dependencies

| Resource | Type | Version | License | CDN URL |
|----------|------|---------|---------|---------|
| Select2 | JavaScript | 4.1.0-rc.0 | MIT | cdn.jsdelivr.net/npm/select2 |
| Select2 Bootstrap Theme | CSS | 1.3.0 | MIT | cdn.jsdelivr.net/npm/select2-bootstrap-5-theme |
| jQuery | JavaScript | 3.6.0 | MIT | code.jquery.com/jquery-3.6.0.min.js |

**Fallback Plan**: If CDN unavailable, basic HTML select elements still function.

---

## Appendix C: Glossary Content Review Notes

**For Human Reviewer**: Please verify the following content for accuracy:

1. **Interaction Type Definitions**
   - [ ] API Integration definition accurate
   - [ ] All 11 types have clear, distinct definitions
   - [ ] Examples represent real-world use cases
   - [ ] Technical indicators are appropriate

2. **Lifecycle Stage Definitions**
   - [ ] All 12 stages align with MaLDReTH II documentation
   - [ ] Activities lists are comprehensive
   - [ ] Typical tools are accurate
   - [ ] Duration estimates reasonable

3. **MaLDReTH Terminology**
   - [ ] Acronyms correctly expanded
   - [ ] Definitions align with RDA documentation
   - [ ] Links to external resources valid

4. **Technical Terms**
   - [ ] Definitions accurate and accessible
   - [ ] No overly technical jargon without explanation
   - [ ] Appropriate for target audience

**Reviewer Notes**: _________________________________

---

## Appendix D: Quick Reference Commands

### Development
```bash
# Start development server
python streamlined_app.py

# Check for syntax errors
python -m py_compile streamlined_app.py

# Find a route
grep -n "def glossary" streamlined_app.py

# Find a template element
grep -rn "search-input" templates/
```

### Testing
```bash
# Test a route
curl http://localhost:5001/glossary | head -20

# Check for JavaScript errors (in browser console)
# Open DevTools > Console

# Validate HTML
# Use browser DevTools > Inspect
```

### Deployment
```bash
# Check Heroku status
heroku ps --app mal2-data-survey-cb27f6674f20

# View logs
heroku logs --tail --app mal2-data-survey-cb27f6674f20

# Backup database
heroku pg:backups:capture --app mal2-data-survey-cb27f6674f20
```

### Rollback
```bash
# View recent commits
git log --oneline -10

# Revert to previous
git revert HEAD

# Force rollback
git reset --hard <commit-hash>
git push heroku main --force
```

---

**END OF PHASE 1 DETAILED IMPLEMENTATION PLAN**

For questions or issues during implementation, refer to the USABILITY_IMPLEMENTATION_PLAN.md or contact the MaLDReTH II working group co-chairs.
