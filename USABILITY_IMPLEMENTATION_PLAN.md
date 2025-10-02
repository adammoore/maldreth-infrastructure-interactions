# PRISM Usability Implementation Plan
**Platform for Research Infrastructure Synergy Mapping**

**Prepared**: October 2025
**Context**: Post-MaLDReTH II Co-chairs Meeting (Sept 25)
**Target**: Brisbane RDA P25 & Ongoing Quality Improvements

---

## Executive Summary

This implementation plan addresses critical usability issues identified through codebase review and user feedback from the September 25 MaLDReTH II co-chairs meeting. The plan prioritizes:

1. **Definition & clarity** - addressing "too much categories - a bit lost"
2. **User guidance** - improving first-time user experience
3. **Feedback mechanisms** - establishing communication channels
4. **Data quality** - ensuring representative, useful interactions

**Timeline**: Phased approach over 8 weeks with quick wins in Week 1-2.

---

## Phase 1: Immediate Fixes (Week 1-2) ⚡

### 1.1 Interaction Type Definitions & Glossary

**Priority**: CRITICAL
**Effort**: 4-6 hours
**Files**:
- Create new: `templates/glossary.html`
- Edit: `templates/streamlined_base.html` (add nav link)
- Edit: `streamlined_app.py` (add route)

**Implementation**:

```python
# Add to streamlined_app.py
INTERACTION_TYPE_DEFINITIONS = {
    'API Integration': {
        'definition': 'Direct programmatic connection between tools using Application Programming Interfaces',
        'example': 'DMPTool connects to RSpace via REST API to sync data management plans',
        'when_to_use': 'When tools communicate programmatically with structured data exchange'
    },
    'Data Exchange': {
        'definition': 'Transfer of research data files or datasets between tools',
        'example': 'Zenodo receives data files exported from GitHub repositories',
        'when_to_use': 'When the primary function is moving data content between systems'
    },
    'Metadata Exchange': {
        'definition': 'Transfer of descriptive information about data without moving the data itself',
        'example': 'ORCID profile information linked to publications in Zenodo',
        'when_to_use': 'When exchanging descriptions, citations, or contextual information'
    },
    'File Format Conversion': {
        'definition': 'Transformation of data from one file format to another',
        'example': 'Converting CSV data to Parquet format for analysis',
        'when_to_use': 'When format transformation is the primary interaction purpose'
    },
    'Workflow Integration': {
        'definition': 'Tools combined into multi-step research workflows or pipelines',
        'example': 'Jupyter Notebook packaged with Docker for reproducible analysis',
        'when_to_use': 'When tools are orchestrated together in a sequence'
    },
    'Plugin/Extension': {
        'definition': 'One tool extends functionality of another through add-ons or plugins',
        'example': 'Zotero plugin installed in Microsoft Word for citation management',
        'when_to_use': 'When one tool adds features directly into another tool\'s interface'
    },
    'Direct Database Connection': {
        'definition': 'Tools query or write to shared database infrastructure',
        'example': 'Analysis tool connects directly to PostgreSQL research database',
        'when_to_use': 'When tools share underlying data storage layer'
    },
    'Web Service': {
        'definition': 'Tools interact via web-based service endpoints (may include APIs)',
        'example': 'Data repository accessed via OAI-PMH harvesting protocol',
        'when_to_use': 'For web-protocol-based interactions like HTTP, SOAP, OAI-PMH'
    },
    'Command Line Interface': {
        'definition': 'Tools invoked or controlled via terminal commands or scripts',
        'example': 'Python script calls FFmpeg via command line to process video data',
        'when_to_use': 'When interaction happens through shell commands or scripts'
    },
    'Import/Export': {
        'definition': 'Manual or semi-automated file-based data transfer between tools',
        'example': 'Export CSV from REDCap, import into R for analysis',
        'when_to_use': 'When users manually transfer files between systems'
    },
    'Other': {
        'definition': 'Interaction types not covered by standard categories',
        'example': 'Custom or novel integration approaches',
        'when_to_use': 'When no other category fits; please describe in Technical Details'
    }
}

@app.route('/glossary')
def glossary():
    """Comprehensive glossary and definitions page."""
    return render_template('glossary.html',
                         interaction_types=INTERACTION_TYPE_DEFINITIONS,
                         lifecycle_stages=MaldrethStage.query.order_by(MaldrethStage.position).all())
```

**HTML Template** (`templates/glossary.html`):
- Create comprehensive glossary page
- Include interaction type definitions with examples
- Lifecycle stage definitions
- MaLDReTH II terminology
- Link from navigation and form pages

**Success Metric**: Users can define interaction types with >80% accuracy in post-implementation testing.

---

### 1.2 Inline Help & Tooltips

**Priority**: HIGH
**Effort**: 3-4 hours
**Files**:
- Edit: `templates/streamlined_add_interaction.html`
- Edit: `static/css/streamlined_style.css`

**Implementation**:

```html
<!-- Add to streamlined_add_interaction.html -->
<div class="col-md-6">
    <label for="interaction_type" class="form-label">
        Interaction Type
        <a href="{{ url_for('glossary') }}#interaction-types" target="_blank"
           class="text-muted ms-1" title="View definitions and examples">
            <i class="fas fa-question-circle"></i>
        </a>
    </label>
    <select class="form-select" id="interaction_type" name="interaction_type" required>
        <option value="">Select interaction type...</option>
        {% for interaction_type in interaction_types %}
        <option value="{{ interaction_type }}"
                title="{{ interaction_type_definitions[interaction_type].definition }}">
            {{ interaction_type }}
        </option>
        {% endfor %}
    </select>
    <div class="form-text" id="interaction-type-hint">
        <small class="text-muted">How do the tools communicate or connect?</small>
    </div>
</div>

<!-- Add Bootstrap tooltips initialization -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Dynamic interaction type help
    document.getElementById('interaction_type').addEventListener('change', function() {
        const selectedType = this.value;
        const hintElement = document.getElementById('interaction-type-hint');
        if (selectedType && interactionTypeDefinitions[selectedType]) {
            hintElement.innerHTML = `<small class="text-info"><i class="fas fa-info-circle"></i> ${interactionTypeDefinitions[selectedType].example}</small>`;
        }
    });
});
</script>
```

**Success Metric**: Reduction in form completion time; decrease in ambiguous interaction type selections.

---

### 1.3 Tool Search/Autocomplete in Dropdowns

**Priority**: CRITICAL
**Effort**: 2-3 hours
**Files**:
- Edit: `templates/streamlined_add_interaction.html`
- Add library: Select2 or similar

**Implementation**:

```html
<!-- Add to head section of streamlined_add_interaction.html -->
<link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
<link href="https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/select2-bootstrap-5-theme.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>

<!-- Replace basic select with searchable select -->
<script>
$(document).ready(function() {
    $('#source_tool_id').select2({
        theme: 'bootstrap-5',
        placeholder: 'Search for a source tool...',
        allowClear: true,
        width: '100%',
        templateResult: formatToolOption,
        templateSelection: formatToolSelection
    });

    $('#target_tool_id').select2({
        theme: 'bootstrap-5',
        placeholder: 'Search for a target tool...',
        allowClear: true,
        width: '100%',
        templateResult: formatToolOption,
        templateSelection: formatToolSelection
    });

    function formatToolOption(tool) {
        if (!tool.id) return tool.text;

        const $tool = $(
            '<span><i class="fas fa-tool me-2"></i>' + tool.text + '</span>'
        );
        return $tool;
    }

    function formatToolSelection(tool) {
        return tool.text;
    }
});
</script>
```

**Success Metric**: Tool selection time reduced by >50%; user satisfaction score increase.

---

### 1.4 CSV Template Download

**Priority**: HIGH
**Effort**: 2 hours
**Files**:
- Edit: `streamlined_app.py` (add route)
- Edit: `templates/streamlined_upload_csv.html`

**Implementation**:

```python
# Add to streamlined_app.py
@app.route('/download/csv-template')
def download_csv_template():
    """Provide a CSV template with example data for users."""

    template_data = [
        {
            'Source Tool': 'GitHub',
            'Target Tool': 'Zenodo',
            'Interaction Type': 'Data Exchange',
            'Lifecycle Stage': 'PRESERVE',
            'Description': 'GitHub repositories archived to Zenodo with DOI assignment',
            'Technical Details': 'GitHub webhook integration, automatic metadata transfer',
            'Benefits': 'Permanent preservation, citable software versions',
            'Challenges': 'Large repository size limits',
            'Examples': 'Software packages automatically archived with each GitHub release',
            'Contact Person': 'Your Name',
            'Organization': 'Your Institution',
            'Email': 'your.email@example.com',
            'Priority': 'medium',
            'Complexity': 'simple',
            'Status': 'implemented',
            'Submitted By': 'Your Name'
        },
        # Add second example row with different interaction type
        {
            'Source Tool': 'REDCap',
            'Target Tool': 'R',
            'Interaction Type': 'API Integration',
            'Lifecycle Stage': 'ANALYSE',
            'Description': 'REDCap provides direct export to R for statistical analysis',
            'Technical Details': 'REDCap API, R packages (REDCapR, redcapAPI)',
            'Benefits': 'Seamless data workflow, reduced manual errors',
            'Challenges': 'Data format conversion complexity',
            'Examples': 'Clinical trial data exported from REDCap for analysis',
            'Contact Person': '',
            'Organization': '',
            'Email': '',
            'Priority': 'high',
            'Complexity': 'moderate',
            'Status': 'implemented',
            'Submitted By': 'Example Contributor'
        }
    ]

    # Create CSV
    output = StringIO()
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
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=prism_interaction_template.csv'

    return response
```

**HTML Addition**:
```html
<!-- Add to templates/streamlined_upload_csv.html -->
<div class="alert alert-info">
    <h5><i class="fas fa-download me-2"></i>Need a Template?</h5>
    <p>Download our CSV template with example interactions to get started:</p>
    <a href="{{ url_for('download_csv_template') }}" class="btn btn-outline-primary">
        <i class="fas fa-file-csv me-2"></i>Download CSV Template
    </a>
</div>
```

**Success Metric**: CSV upload success rate increases; fewer validation errors.

---

### 1.5 Basic Search on Interactions Table

**Priority**: HIGH
**Effort**: 2-3 hours
**Files**:
- Edit: `templates/streamlined_view_interactions.html`

**Implementation**:

```html
<!-- Add before table in streamlined_view_interactions.html -->
<div class="card mb-3">
    <div class="card-body">
        <div class="row g-3">
            <div class="col-md-4">
                <label for="search-input" class="form-label">Search Interactions</label>
                <input type="text" class="form-control" id="search-input"
                       placeholder="Search by tool name, description...">
            </div>
            <div class="col-md-3">
                <label for="filter-type" class="form-label">Interaction Type</label>
                <select class="form-select" id="filter-type">
                    <option value="">All Types</option>
                    {% for interaction_type in interaction_types %}
                    <option value="{{ interaction_type }}">{{ interaction_type }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label for="filter-stage" class="form-label">Lifecycle Stage</label>
                <select class="form-select" id="filter-stage">
                    <option value="">All Stages</option>
                    {% for stage in stages %}
                    <option value="{{ stage.name }}">{{ stage.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2 d-flex align-items-end">
                <button class="btn btn-outline-secondary w-100" id="clear-filters">
                    <i class="fas fa-times me-1"></i>Clear
                </button>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const filterType = document.getElementById('filter-type');
    const filterStage = document.getElementById('filter-stage');
    const clearButton = document.getElementById('clear-filters');
    const tableRows = document.querySelectorAll('tbody tr');

    function filterTable() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedType = filterType.value.toLowerCase();
        const selectedStage = filterStage.value.toLowerCase();

        let visibleCount = 0;

        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matchesSearch = !searchTerm || text.includes(searchTerm);
            const matchesType = !selectedType || text.includes(selectedType);
            const matchesStage = !selectedStage || text.includes(selectedStage);

            if (matchesSearch && matchesType && matchesStage) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Update result count
        updateResultCount(visibleCount);
    }

    function updateResultCount(count) {
        let countElement = document.getElementById('result-count');
        if (!countElement) {
            countElement = document.createElement('div');
            countElement.id = 'result-count';
            countElement.className = 'text-muted mb-2';
            document.querySelector('.table-responsive').insertBefore(countElement, document.querySelector('table'));
        }
        countElement.textContent = `Showing ${count} interaction(s)`;
    }

    searchInput.addEventListener('keyup', filterTable);
    filterType.addEventListener('change', filterTable);
    filterStage.addEventListener('change', filterTable);

    clearButton.addEventListener('click', function() {
        searchInput.value = '';
        filterType.value = '';
        filterStage.value = '';
        filterTable();
    });

    // Initialize count
    updateResultCount(tableRows.length);
});
</script>
```

**Success Metric**: Users can find specific interactions in <10 seconds.

---

## Phase 2: User Guidance Improvements (Week 3-4) 📚

### 2.1 First-Time User Welcome Modal

**Priority**: HIGH
**Effort**: 4-5 hours
**Files**:
- Edit: `templates/streamlined_index.html`
- Edit: `static/css/streamlined_style.css`

**Implementation**:

```html
<!-- Add to streamlined_index.html, before {% endblock %} -->
<!-- First-Time User Welcome Modal -->
<div class="modal fade" id="welcomeModal" tabindex="-1" aria-labelledby="welcomeModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title" id="welcomeModalLabel">
                    <i class="fas fa-rocket me-2"></i>Welcome to PRISM!
                </h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6 class="text-primary">What is PRISM?</h6>
                        <p class="small">
                            <strong>Platform for Research Infrastructure Synergy Mapping</strong> helps you
                            map and understand how digital research tools interact across the research data lifecycle.
                        </p>
                        <h6 class="text-primary mt-3">Why Contribute?</h6>
                        <ul class="small">
                            <li>Build comprehensive tool interaction knowledge</li>
                            <li>Support FAIR data practices</li>
                            <li>Help researchers discover tool integrations</li>
                            <li>Contribute to RDA MaLDReTH II initiative</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6 class="text-primary">Quick Start Guide</h6>
                        <ol class="small">
                            <li><strong>Explore</strong>: Browse existing interactions and lifecycle stages</li>
                            <li><strong>Learn</strong>: Read the <a href="{{ url_for('glossary') }}" target="_blank">glossary</a> to understand terminology</li>
                            <li><strong>Contribute</strong>: Add interactions you know about</li>
                            <li><strong>Share</strong>: Export data or use the API</li>
                        </ol>

                        <div class="alert alert-info border-0 mt-3">
                            <small>
                                <i class="fas fa-lightbulb me-1"></i>
                                <strong>Tip:</strong> Start by browsing the
                                <a href="{{ url_for('view_interactions') }}">existing interactions</a>
                                to see examples!
                            </small>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <div class="form-check me-auto">
                    <input class="form-check-input" type="checkbox" id="dontShowAgain">
                    <label class="form-check-label small" for="dontShowAgain">
                        Don't show this again
                    </label>
                </div>
                <a href="{{ url_for('glossary') }}" class="btn btn-outline-primary">
                    <i class="fas fa-book me-1"></i>View Glossary
                </a>
                <a href="{{ url_for('add_interaction') }}" class="btn btn-primary">
                    <i class="fas fa-plus me-1"></i>Add Interaction
                </a>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Check if user has dismissed welcome modal before
    const hasSeenWelcome = localStorage.getItem('prism_welcome_seen');

    if (!hasSeenWelcome) {
        const welcomeModal = new bootstrap.Modal(document.getElementById('welcomeModal'));
        welcomeModal.show();
    }

    // Handle "don't show again" checkbox
    document.getElementById('dontShowAgain').addEventListener('change', function() {
        if (this.checked) {
            localStorage.setItem('prism_welcome_seen', 'true');
        } else {
            localStorage.removeItem('prism_welcome_seen');
        }
    });
});
</script>
```

**Success Metric**: Increased engagement from first-time visitors; reduced bounce rate.

---

### 2.2 Example Interactions Showcase

**Priority**: MEDIUM
**Effort**: 3-4 hours
**Files**:
- Edit: `streamlined_app.py` (add route, flagging system)
- Create: `templates/examples.html`

**Implementation**:

```python
# Add to ToolInteraction model in streamlined_app.py
class ToolInteraction(db.Model):
    # ... existing fields ...
    is_featured = db.Column(db.Boolean, default=False)  # Add this field
    featured_reason = db.Column(db.String(200))  # Why this is a good example

# Add route
@app.route('/examples')
def examples():
    """Showcase featured/exemplar interactions."""
    featured = ToolInteraction.query.filter_by(is_featured=True).all()

    # If no featured interactions, show highest quality ones
    if not featured:
        featured = ToolInteraction.query.filter(
            ToolInteraction.description.isnot(None),
            ToolInteraction.technical_details.isnot(None),
            ToolInteraction.examples.isnot(None)
        ).limit(6).all()

    return render_template('examples.html', interactions=featured)
```

**HTML Template**:
- Create gallery view of exemplar interactions
- Annotate why each is a good example
- Link from glossary and add interaction pages
- Include "Submit yours" call-to-action

**Success Metric**: Improved quality of new submissions (completeness score).

---

### 2.3 Progressive Form Disclosure

**Priority**: MEDIUM
**Effort**: 5-6 hours
**Files**:
- Edit: `templates/streamlined_add_interaction.html`

**Implementation**:

```html
<!-- Reorganize form with collapsible sections -->
<form method="POST" action="{{ url_for('add_interaction') }}">

    <!-- Always visible: Required fields -->
    <div class="card mb-3">
        <div class="card-header bg-primary text-white">
            <h5 class="mb-0"><i class="fas fa-asterisk me-2"></i>Required Information</h5>
        </div>
        <div class="card-body">
            <!-- Source/Target tools, Type, Stage, Description -->
        </div>
    </div>

    <!-- Collapsible: Technical Details -->
    <div class="card mb-3">
        <div class="card-header" style="cursor: pointer;" data-bs-toggle="collapse" data-bs-target="#technicalSection">
            <h5 class="mb-0">
                <i class="fas fa-caret-right me-2" id="tech-icon"></i>
                Technical Details
                <span class="badge bg-secondary">Optional</span>
            </h5>
        </div>
        <div id="technicalSection" class="collapse">
            <div class="card-body">
                <!-- Technical details, benefits, challenges, examples -->
            </div>
        </div>
    </div>

    <!-- Collapsible: Contact Information -->
    <div class="card mb-3">
        <div class="card-header" style="cursor: pointer;" data-bs-toggle="collapse" data-bs-target="#contactSection">
            <h5 class="mb-0">
                <i class="fas fa-caret-right me-2" id="contact-icon"></i>
                Contact Information
                <span class="badge bg-secondary">Optional</span>
            </h5>
        </div>
        <div id="contactSection" class="collapse">
            <div class="card-body">
                <!-- Contact person, org, email -->
            </div>
        </div>
    </div>

    <!-- Collapsible: Classification -->
    <div class="card mb-3">
        <div class="card-header" style="cursor: pointer;" data-bs-toggle="collapse" data-bs-target="#classificationSection">
            <h5 class="mb-0">
                <i class="fas fa-caret-right me-2" id="class-icon"></i>
                Classification
                <span class="badge bg-secondary">Optional</span>
            </h5>
        </div>
        <div id="classificationSection" class="collapse">
            <div class="card-body">
                <!-- Priority, complexity, status -->
            </div>
        </div>
    </div>

    <!-- Submitter (always visible) -->
    <div class="mb-3">
        <label for="submitted_by" class="form-label">Your Name (Optional)</label>
        <input type="text" class="form-control" id="submitted_by" name="submitted_by">
    </div>

    <!-- Submit Button -->
    <div class="d-grid">
        <button type="submit" class="btn btn-primary btn-lg">Submit Interaction</button>
    </div>
</form>

<script>
// Toggle caret icons on collapse
document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(element => {
    element.addEventListener('click', function() {
        const icon = this.querySelector('.fa-caret-right, .fa-caret-down');
        if (icon) {
            icon.classList.toggle('fa-caret-right');
            icon.classList.toggle('fa-caret-down');
        }
    });
});
</script>
```

**Success Metric**: Form completion rate increases; time to complete required fields decreases.

---

### 2.4 Field Examples & Placeholders

**Priority**: MEDIUM
**Effort**: 2 hours
**Files**:
- Edit: `templates/streamlined_add_interaction.html`

**Implementation**:

```html
<!-- Enhanced placeholders with examples -->
<div class="mb-3">
    <label for="description" class="form-label">
        Description
        <small class="text-muted">(What happens in this interaction?)</small>
    </label>
    <textarea class="form-control" id="description" name="description" rows="3"
              placeholder="Example: Zenodo automatically links publications to ORCID profiles, enabling comprehensive research output tracking and attribution across the scholarly ecosystem."
              required></textarea>
    <div class="form-text">
        <small>Describe what the interaction does and why it's useful. Aim for 1-3 sentences.</small>
    </div>
</div>

<div class="mb-3">
    <label for="technical_details" class="form-label">
        Technical Implementation
        <small class="text-muted">(How does it work technically?)</small>
    </label>
    <textarea class="form-control" id="technical_details" name="technical_details" rows="2"
              placeholder="Example: REST API integration with ORCID authentication, DOI-based linking"></textarea>
    <div class="form-text">
        <small>Mention protocols, APIs, standards, or technologies used.</small>
    </div>
</div>

<div class="mb-3">
    <label for="benefits" class="form-label">
        Benefits
        <small class="text-muted">(What are the advantages?)</small>
    </label>
    <textarea class="form-control" id="benefits" name="benefits" rows="2"
              placeholder="Example: Enhanced researcher visibility, automated attribution, improved discoverability"></textarea>
    <div class="form-text">
        <small>List key advantages or improvements this interaction provides.</small>
    </div>
</div>
```

**Success Metric**: Higher quality submissions with complete information.

---

## Phase 3: Feedback & Communication (Week 5-6) 💬

### 3.1 In-App Feedback Mechanism

**Priority**: HIGH
**Effort**: 4-5 hours
**Files**:
- Create: `templates/feedback.html`
- Edit: `streamlined_app.py` (add model, routes)
- Edit: `templates/streamlined_base.html` (add feedback link)

**Implementation**:

```python
# Add to streamlined_app.py

class UserFeedback(db.Model):
    """Model for collecting user feedback and suggestions."""
    __tablename__ = 'user_feedback'
    id = db.Column(db.Integer, primary_key=True)
    feedback_type = db.Column(db.String(50))  # bug, feature, usability, other
    page_url = db.Column(db.String(500))
    subject = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=False)
    user_name = db.Column(db.String(100))
    user_email = db.Column(db.String(200))
    status = db.Column(db.String(50), default='new')  # new, reviewing, resolved
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """User feedback submission page."""
    if request.method == 'POST':
        feedback = UserFeedback(
            feedback_type=request.form.get('feedback_type'),
            page_url=request.form.get('page_url'),
            subject=request.form.get('subject'),
            description=request.form.get('description'),
            user_name=request.form.get('user_name'),
            user_email=request.form.get('user_email')
        )

        db.session.add(feedback)
        db.session.commit()

        flash('Thank you for your feedback! We review all submissions.', 'success')
        return redirect(url_for('index'))

    return render_template('feedback.html',
                         referrer=request.referrer or url_for('index'))

@app.route('/feedback/view')
def view_feedback():
    """Admin view of feedback (add authentication in production)."""
    feedback_items = UserFeedback.query.order_by(UserFeedback.submitted_at.desc()).all()
    return render_template('feedback_admin.html', feedback=feedback_items)
```

**HTML Template** (`templates/feedback.html`):
```html
{% extends "streamlined_base.html" %}

{% block title %}Feedback - PRISM{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card border-0 shadow">
                <div class="card-header bg-primary text-white">
                    <h3 class="mb-0"><i class="fas fa-comment-dots me-2"></i>Share Your Feedback</h3>
                </div>
                <div class="card-body">
                    <p class="lead">
                        Help us improve PRISM! Your feedback is essential to making this platform
                        more useful for the research community.
                    </p>

                    <form method="POST" action="{{ url_for('feedback') }}">
                        <input type="hidden" name="page_url" value="{{ referrer }}">

                        <div class="mb-3">
                            <label for="feedback_type" class="form-label">Type of Feedback</label>
                            <select class="form-select" id="feedback_type" name="feedback_type" required>
                                <option value="">Select feedback type...</option>
                                <option value="bug">🐛 Bug Report</option>
                                <option value="feature">💡 Feature Request</option>
                                <option value="usability">👤 Usability Issue</option>
                                <option value="content">📝 Content/Data Issue</option>
                                <option value="other">💬 Other</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="subject" class="form-label">Subject</label>
                            <input type="text" class="form-control" id="subject"
                                   name="subject" placeholder="Brief description" required>
                        </div>

                        <div class="mb-3">
                            <label for="description" class="form-label">Details</label>
                            <textarea class="form-control" id="description" name="description"
                                      rows="5" placeholder="Please provide as much detail as possible..."
                                      required></textarea>
                        </div>

                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label for="user_name" class="form-label">Your Name (Optional)</label>
                                <input type="text" class="form-control" id="user_name" name="user_name">
                            </div>
                            <div class="col-md-6">
                                <label for="user_email" class="form-label">Email (Optional)</label>
                                <input type="email" class="form-control" id="user_email" name="user_email"
                                       placeholder="If you'd like a response">
                            </div>
                        </div>

                        <div class="alert alert-info border-0">
                            <small>
                                <i class="fas fa-info-circle me-1"></i>
                                All feedback is reviewed by the MaLDReTH II team. For urgent issues,
                                please contact the working group directly.
                            </small>
                        </div>

                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="{{ referrer }}" class="btn btn-outline-secondary">Cancel</a>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-paper-plane me-2"></i>Submit Feedback
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Alternative feedback channels -->
            <div class="card border-0 shadow mt-4">
                <div class="card-body">
                    <h5 class="card-title">Other Ways to Connect</h5>
                    <ul class="list-unstyled">
                        <li class="mb-2">
                            <i class="fas fa-users me-2 text-primary"></i>
                            Join the <a href="https://www.rd-alliance.org/groups/mapping-the-landscape-of-digital-research-tools-ii-maldreth-ii" target="_blank">MaLDReTH II Working Group</a>
                        </li>
                        <li class="mb-2">
                            <i class="fab fa-github me-2 text-dark"></i>
                            Report issues on <a href="https://github.com/adammoore/maldreth-infrastructure-interactions/issues" target="_blank">GitHub</a>
                        </li>
                        <li>
                            <i class="fas fa-envelope me-2 text-success"></i>
                            Email the working group coordinators
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**Navigation Link** (add to `templates/streamlined_base.html`):
```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('feedback') }}">
        <i class="fas fa-comment-dots me-1"></i>Feedback
    </a>
</li>
```

**Success Metric**: Collect 20+ feedback submissions within first month; actionable insights identified.

---

### 3.2 Floating Feedback Button

**Priority**: LOW
**Effort**: 1-2 hours
**Files**:
- Edit: `templates/streamlined_base.html`
- Edit: `static/css/streamlined_style.css`

**Implementation**:

```html
<!-- Add to streamlined_base.html before </body> -->
<a href="{{ url_for('feedback') }}" class="floating-feedback-btn"
   title="Share your feedback">
    <i class="fas fa-comment-dots"></i>
    <span class="d-none d-md-inline ms-2">Feedback</span>
</a>
```

```css
/* Add to streamlined_style.css */
.floating-feedback-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #667eea;
    color: white;
    padding: 12px 20px;
    border-radius: 50px;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    text-decoration: none;
    font-weight: 600;
    z-index: 1000;
    transition: all 0.3s ease;
}

.floating-feedback-btn:hover {
    background: #5568d3;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

.floating-feedback-btn i {
    font-size: 18px;
}
```

**Success Metric**: Increased feedback submission rate.

---

## Phase 4: Data Quality & Visualization (Week 7-8) 📊

### 4.1 Interaction Completeness Indicator

**Priority**: MEDIUM
**Effort**: 3-4 hours
**Files**:
- Edit: `streamlined_app.py` (add property to model)
- Edit: `templates/streamlined_view_interactions.html`
- Edit: `templates/streamlined_interaction_detail.html`

**Implementation**:

```python
# Add to ToolInteraction model
@property
def completeness_score(self):
    """Calculate how complete this interaction record is (0-100)."""
    score = 0
    total_fields = 15

    # Required fields (already have these)
    score += 4  # source_tool, target_tool, interaction_type, lifecycle_stage, description

    # Optional but valuable fields
    if self.technical_details and len(self.technical_details) > 20:
        score += 1
    if self.benefits and len(self.benefits) > 20:
        score += 1
    if self.challenges and len(self.challenges) > 20:
        score += 1
    if self.examples and len(self.examples) > 20:
        score += 1
    if self.contact_person:
        score += 1
    if self.organization:
        score += 1
    if self.email:
        score += 1
    if self.priority:
        score += 1
    if self.complexity:
        score += 1
    if self.status:
        score += 1
    if self.submitted_by:
        score += 1

    return int((score / total_fields) * 100)

@property
def quality_badge(self):
    """Return a quality badge class based on completeness."""
    score = self.completeness_score
    if score >= 80:
        return 'success'  # Green - Excellent
    elif score >= 60:
        return 'info'     # Blue - Good
    elif score >= 40:
        return 'warning'  # Yellow - Fair
    else:
        return 'secondary' # Gray - Minimal
```

**Display in Templates**:
```html
<!-- Add to interaction detail view -->
<div class="card mb-3">
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Record Completeness</h6>
            <span class="badge bg-{{ interaction.quality_badge }} fs-6">
                {{ interaction.completeness_score }}% Complete
            </span>
        </div>
        <div class="progress mt-2" style="height: 8px;">
            <div class="progress-bar bg-{{ interaction.quality_badge }}"
                 role="progressbar"
                 style="width: {{ interaction.completeness_score }}%"
                 aria-valuenow="{{ interaction.completeness_score }}"
                 aria-valuemin="0"
                 aria-valuemax="100"></div>
        </div>
        <small class="text-muted mt-1 d-block">
            {% if interaction.completeness_score < 60 %}
                Consider adding more details to help others understand this interaction.
                <a href="{{ url_for('edit_interaction', interaction_id=interaction.id) }}">
                    Edit interaction
                </a>
            {% else %}
                This is a high-quality interaction record!
            {% endif %}
        </small>
    </div>
</div>
```

**Success Metric**: Average completeness score increases over time; users enhance existing records.

---

### 4.2 Enhanced Information Structures Page

**Priority**: MEDIUM
**Effort**: 4-5 hours
**Files**:
- Edit: `templates/information_structures.html`

**Implementation**: Add interactive statistics and charts
- Interaction type distribution (bar chart)
- Lifecycle stage coverage (donut chart)
- Tool connectivity graph (network stats)
- Recent activity timeline
- Quality metrics dashboard

**Success Metric**: Users understand database structure and coverage better.

---

### 4.3 Pagination on Views

**Priority**: MEDIUM
**Effort**: 3 hours
**Files**:
- Edit: `streamlined_app.py` (update view routes)
- Edit: `templates/streamlined_view_interactions.html`

**Implementation**:

```python
# Update route in streamlined_app.py
@app.route('/view/interactions')
def view_interactions():
    """View all tool interactions with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    pagination = ToolInteraction.query.order_by(
        ToolInteraction.submitted_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template('streamlined_view_interactions.html',
                         interactions=pagination.items,
                         pagination=pagination,
                         interaction_types=INTERACTION_TYPES,
                         stages=MaldrethStage.query.order_by(MaldrethStage.position).all())
```

```html
<!-- Add pagination controls to template -->
{% if pagination.pages > 1 %}
<nav aria-label="Interaction pagination" class="mt-4">
    <ul class="pagination justify-content-center">
        <li class="page-item {% if not pagination.has_prev %}disabled{% endif %}">
            <a class="page-link" href="{{ url_for('view_interactions', page=pagination.prev_num) }}">
                Previous
            </a>
        </li>

        {% for page_num in pagination.iter_pages(left_edge=1, right_edge=1, left_current=2, right_current=2) %}
            {% if page_num %}
                <li class="page-item {% if page_num == pagination.page %}active{% endif %}">
                    <a class="page-link" href="{{ url_for('view_interactions', page=page_num) }}">
                        {{ page_num }}
                    </a>
                </li>
            {% else %}
                <li class="page-item disabled"><span class="page-link">...</span></li>
            {% endif %}
        {% endfor %}

        <li class="page-item {% if not pagination.has_next %}disabled{% endif %}">
            <a class="page-link" href="{{ url_for('view_interactions', page=pagination.next_num) }}">
                Next
            </a>
        </li>
    </ul>

    <div class="text-center text-muted">
        <small>
            Showing {{ pagination.first }} - {{ pagination.last }} of {{ pagination.total }} interactions
        </small>
    </div>
</nav>
{% endif %}
```

**Success Metric**: Improved performance with large datasets; better user experience browsing interactions.

---

### 4.4 Duplicate Detection During Manual Entry

**Priority**: LOW
**Effort**: 4 hours
**Files**:
- Edit: `streamlined_app.py` (add interaction endpoint)
- Edit: `templates/streamlined_add_interaction.html`

**Implementation**: AJAX check for similar interactions when user selects tools
- When source + target tools selected, query for existing interactions
- Show warning: "Similar interaction exists: [link]"
- Allow user to proceed or view existing

**Success Metric**: Reduction in duplicate interactions created.

---

## Phase 5: Content & Documentation (Week 9-10) 📖

### 5.1 Comprehensive Glossary Page

**Priority**: HIGH
**Effort**: 6-8 hours (content creation)
**Files**:
- Create: `templates/glossary.html`
- Edit: `streamlined_app.py`

**Content Sections**:

1. **Interaction Types** (definitions from 1.1 above)
2. **Lifecycle Stages**
   - CONCEPTUALISE: Initial research idea formation and hypothesis development
   - PLAN: Research design, methodology planning, and resource allocation
   - FUND: Grant applications and resource acquisition
   - COLLECT: Data gathering and experimental execution
   - PROCESS: Data cleaning, quality control, and preparation
   - ANALYSE: Statistical analysis and interpretation
   - STORE: Short-term data storage during active research
   - PUBLISH: Dissemination through journals, conferences, preprints
   - PRESERVE: Long-term archival and curation
   - SHARE: Making data accessible to others
   - ACCESS: Discovery and retrieval of data by users
   - TRANSFORM: Data reuse, repurposing, and derivative works

3. **MaLDReTH Terminology**
   - MaLDReTH: Mapping the Landscape of Digital Research Tools Harmonised
   - PRISM: Platform for Research Infrastructure Synergy Mapping
   - Exemplar Tool: Representative tool within a category
   - Tool Category: Classification group for similar tools
   - Tool Interaction: Connection or integration between tools
   - Research Data Lifecycle (RDL): 12-stage model of research workflow

4. **Technical Terms**
   - API: Application Programming Interface
   - REST: Representational State Transfer
   - OAuth: Open Authorization
   - DOI: Digital Object Identifier
   - ORCID: Open Researcher and Contributor ID
   - FAIR: Findable, Accessible, Interoperable, Reusable

5. **Contributing Guide**
   - How to add an interaction
   - What makes a good interaction description
   - CSV bulk upload instructions
   - Quality expectations

**Success Metric**: Glossary page becomes most-visited resource; terminology confusion decreases.

---

### 5.2 FAQ Section

**Priority**: MEDIUM
**Effort**: 4 hours
**Files**:
- Edit: `templates/about.html` (add FAQ accordion)

**Sample FAQs**:
- What is PRISM and how does it relate to MaLDReTH?
- How do I choose the right interaction type?
- Can I edit an interaction I submitted?
- How is this different from other tool catalogs?
- What happens to the data I contribute?
- How can I cite PRISM?
- Who maintains this platform?

**Success Metric**: Reduced support requests; self-service question resolution.

---

### 5.3 Video Tutorial / Walkthrough

**Priority**: LOW
**Effort**: 8-12 hours
**Deliverables**:
- 3-5 minute intro video
- Screen recordings of key tasks
- Embedded on homepage and about page

**Success Metric**: Video views correlate with successful submissions.

---

## Implementation Timeline

```
Week 1-2: Quick Wins (Phase 1)
├── Day 1-2: Interaction type definitions & glossary structure
├── Day 3-4: Tooltips and inline help
├── Day 5-6: Tool search/autocomplete
├── Day 7-8: CSV template & basic search
└── Day 9-10: Testing and refinement

Week 3-4: User Guidance (Phase 2)
├── Day 1-3: Welcome modal & onboarding
├── Day 4-5: Example interactions showcase
├── Day 6-8: Progressive form disclosure
└── Day 9-10: Field examples and help text

Week 5-6: Feedback Mechanisms (Phase 3)
├── Day 1-4: In-app feedback system
├── Day 5-6: Floating feedback button
├── Day 7-8: Feedback review dashboard
└── Day 9-10: Testing with users

Week 7-8: Data Quality (Phase 4)
├── Day 1-3: Completeness indicator
├── Day 4-6: Enhanced information structures
├── Day 7-8: Pagination
└── Day 9-10: Duplicate detection

Week 9-10: Documentation (Phase 5)
├── Day 1-5: Comprehensive glossary content
├── Day 6-8: FAQ section
└── Day 9-10: Video tutorials (optional)
```

---

## Success Metrics & KPIs

### User Engagement
- [ ] First-time user completion rate >70%
- [ ] Return user rate increase by 25%
- [ ] Average session duration increase
- [ ] Bounce rate decrease by 30%

### Data Quality
- [ ] Average interaction completeness >65%
- [ ] Percentage of interactions with technical details >50%
- [ ] Duplicate submissions <5%
- [ ] Monthly interaction additions increase by 40%

### Usability
- [ ] Task completion time for adding interaction <5 minutes
- [ ] Tool selection time <30 seconds
- [ ] Search success rate >90%
- [ ] User satisfaction score >4/5

### Support & Feedback
- [ ] 20+ feedback submissions in first month
- [ ] <10% of feedback reports critical bugs
- [ ] Response to feedback within 7 days
- [ ] User testing participation rate >15%

---

## Testing Protocol

### Pre-Implementation Testing
1. **Baseline Usability Study** (5 users)
   - Time to complete first interaction
   - Points of confusion
   - Help requests
   - Completion vs abandonment

### During Implementation
2. **A/B Testing**
   - Progressive form vs full form
   - With/without tooltips
   - Welcome modal vs no modal

3. **Feature Testing** (after each phase)
   - Functionality testing
   - Cross-browser compatibility
   - Mobile responsiveness
   - Performance impact

### Post-Implementation
4. **Follow-up Usability Study** (5 users)
   - Repeat baseline tasks
   - Measure improvements
   - Collect qualitative feedback

5. **Analytics Monitoring**
   - Google Analytics event tracking
   - Heatmap analysis (Hotjar or similar)
   - Form abandonment tracking

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| User resistance to changes | Medium | Phased rollout; welcome modal explains changes |
| Performance degradation | High | Pagination; optimize queries; caching |
| Increased complexity | Medium | Progressive disclosure; clear navigation |
| Database migration issues | High | Test migrations in staging; backup before deploy |
| Browser compatibility | Medium | Test on Chrome, Firefox, Safari, Edge |
| Mobile experience degraded | Medium | Responsive design testing; mobile-first approach |

---

## Brisbane RDA P25 Preparation

### Pre-Conference (Before Brisbane)
- [ ] Complete Phase 1 (Quick Wins)
- [ ] Draft glossary with community input
- [ ] Gather feedback via new mechanism
- [ ] Identify 5-6 exemplar interactions per category
- [ ] Prepare demo scenarios for presentation

### At Conference
- [ ] Live demo of new features
- [ ] Facilitated usability testing session
- [ ] Glossary review workshop
- [ ] Collect feedback on interaction instances
- [ ] Document feature requests

### Post-Conference
- [ ] Implement priority feedback
- [ ] Complete remaining phases
- [ ] Publish conference insights
- [ ] Expand exemplar interaction library

---

## Resource Requirements

### Development Time
- Phase 1: 16-20 hours
- Phase 2: 18-22 hours
- Phase 3: 10-14 hours
- Phase 4: 14-18 hours
- Phase 5: 18-28 hours

**Total**: 76-102 hours (approximately 2-3 weeks full-time)

### Tools & Services
- Select2 library (free, MIT license)
- Bootstrap 5 (already in use)
- Optional: Hotjar or similar for heatmaps ($0-39/month)
- Optional: Video hosting (YouTube - free)

### Community Involvement
- Glossary content review (MaLDReTH II co-chairs)
- Usability testing participants (5-10 volunteers)
- Example interaction curation (working group members)
- Video narration/script review (optional)

---

## Maintenance Plan

### Ongoing Tasks
- **Weekly**: Review feedback submissions
- **Bi-weekly**: Update glossary based on user questions
- **Monthly**: Review analytics and metrics
- **Quarterly**: Usability testing session
- **Annually**: Comprehensive UX audit

### Content Updates
- Add new interaction types as needed
- Update examples with current use cases
- Refresh video tutorials annually
- Expand FAQ based on common questions

---

## Appendix A: Implementation Checklist

### Phase 1: Immediate Fixes
- [ ] 1.1 Interaction type definitions & glossary route
- [ ] 1.2 Inline help & tooltips on forms
- [ ] 1.3 Tool search/autocomplete (Select2)
- [ ] 1.4 CSV template download endpoint
- [ ] 1.5 Basic search on interactions table

### Phase 2: User Guidance
- [ ] 2.1 First-time user welcome modal
- [ ] 2.2 Example interactions showcase
- [ ] 2.3 Progressive form disclosure
- [ ] 2.4 Field examples & enhanced placeholders

### Phase 3: Feedback
- [ ] 3.1 Feedback model & submission system
- [ ] 3.2 Floating feedback button
- [ ] 3.3 Feedback admin dashboard
- [ ] 3.4 Feedback notification system

### Phase 4: Data Quality
- [ ] 4.1 Interaction completeness indicator
- [ ] 4.2 Enhanced information structures page
- [ ] 4.3 Pagination on views
- [ ] 4.4 Duplicate detection during entry

### Phase 5: Documentation
- [ ] 5.1 Comprehensive glossary content
- [ ] 5.2 FAQ section
- [ ] 5.3 Video tutorials (optional)

---

## Appendix B: User Testing Scripts

### Script 1: First Interaction Submission
**Task**: "Please add an interaction between two research tools you're familiar with."

**Observe**:
- Time to complete
- Fields causing confusion
- Help requests
- Completion vs abandonment

**Post-Task Questions**:
1. What was most confusing?
2. What information did you wish you had?
3. Would you submit another interaction?

### Script 2: Finding Information
**Task**: "Find all API integrations in the PLAN stage."

**Observe**:
- Search strategy
- Success/failure
- Time to complete
- Frustration points

### Script 3: Understanding PRISM
**Task**: "Explain what PRISM is for and who should use it."

**Assess**:
- Comprehension of purpose
- Value proposition understanding
- Target audience clarity

---

## Appendix C: Feedback Form Template

```
PRISM User Feedback

Date: [auto-filled]
Page: [auto-filled from referrer]

Type: [ ] Bug  [ ] Feature Request  [ ] Usability  [ ] Content  [ ] Other

Subject: _______________________

Description:
_______________________
_______________________

Your Name (optional): _______________________
Email (optional): _______________________

[Submit Feedback]
```

---

**END OF IMPLEMENTATION PLAN**

For questions or clarifications, contact the MaLDReTH II working group co-chairs or submit feedback via the PRISM platform.
