# PRISM Implementation Roadmap

**Comprehensive plan for Discovery System, Admin Role, and Data Quality Improvements**

---

## Current State Assessment

### ✅ Completed
- Core PRISM application with 12-stage lifecycle
- Tool and interaction management
- Multiple visualization modes (radial, circular, network, matrix)
- CSV import for interactions
- Basic tool CSV upload (needs fixes)
- External catalog documentation

### ⚠️ Needs Fixes
- Tool CSV upload route (missing fields: license, github_url, notes)
- Interaction CSV upload (func import error)
- Tool model lacks fields for enrichment data
- No admin role or curation workflow
- No delete/reject functionality

### 🎯 To Build
- Discovery system with queue
- Admin authentication and authorization
- Curation/approval workflows
- Enhanced tool model with full metadata

---

## Phase 1: Critical Fixes (Week 1)

**Priority: URGENT** - Fix broken functionality

### 1.1 Fix Database Schema Issues
**Tasks:**
- [ ] Add missing fields to ExemplarTool model
- [ ] Create database migration
- [ ] Update tool CSV upload to use new fields
- [ ] Fix `func` import error in interactions upload

**Files to Modify:**
- `streamlined_app.py` - ExemplarTool model
- Create new migration file
- `streamlined_app.py` - Tool CSV route

**Estimated Time:** 2 days

### 1.2 Fix CSV Import Functionality
**Tasks:**
- [ ] Add missing import: `from sqlalchemy import func`
- [ ] Test interaction CSV upload with enriched_interactions_catalog.csv
- [ ] Test tool CSV upload with enriched_tools_catalog.csv
- [ ] Document any remaining limitations

**Files to Modify:**
- `streamlined_app.py` - Add import statement
- Test both CSV uploads

**Estimated Time:** 1 day

### 1.3 Add Navigation Links
**Tasks:**
- [ ] Add "Upload Tools CSV" link to navigation menu
- [ ] Create CSV Tools dropdown with both upload options
- [ ] Update documentation to explain both upload routes

**Files to Modify:**
- `templates/streamlined_base.html` - Navigation
- `README.md` - Update documentation

**Estimated Time:** 0.5 days

### Deliverables:
- ✅ Working tool and interaction CSV imports
- ✅ Full metadata support for enriched catalogs
- ✅ Clear navigation to all upload features

---

## Phase 2: Admin Role & Authentication (Week 2)

**Priority: HIGH** - Required for curation workflows

### 2.1 Add User Authentication System
**Tasks:**
- [ ] Install Flask-Login
- [ ] Create User model
- [ ] Implement login/logout routes
- [ ] Add session management
- [ ] Create login template

**Database Schema:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',  -- viewer, editor, admin
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**Files to Create:**
- `models/user.py` - User model
- `auth/__init__.py` - Auth blueprint
- `auth/routes.py` - Login/logout routes
- `templates/auth/login.html` - Login page
- `templates/auth/register.html` - Registration (admin only)

**Estimated Time:** 3 days

### 2.2 Implement Role-Based Access Control
**Tasks:**
- [ ] Create role decorator (`@requires_role('admin')`)
- [ ] Protect admin routes
- [ ] Add role checks to templates
- [ ] Create permissions matrix

**Permissions Matrix:**
| Action | Viewer | Editor | Admin |
|--------|--------|--------|-------|
| View tools/interactions | ✅ | ✅ | ✅ |
| Add interactions | ✅ | ✅ | ✅ |
| Edit interactions | ❌ | ✅ | ✅ |
| Delete interactions | ❌ | ❌ | ✅ |
| Upload CSV | ❌ | ✅ | ✅ |
| Review discoveries | ❌ | ✅ | ✅ |
| Approve discoveries | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

**Files to Modify:**
- `streamlined_app.py` - Add role decorators
- All templates - Show/hide actions based on role
- `templates/streamlined_base.html` - Show login status

**Estimated Time:** 2 days

### Deliverables:
- ✅ User authentication with roles
- ✅ Role-based access control
- ✅ Protected admin functions

---

## Phase 3: Curation & Moderation Tools (Week 3)

**Priority: HIGH** - Enable quality control

### 3.1 Add Delete/Archive Functionality
**Tasks:**
- [ ] Add "archived" field to interactions and tools
- [ ] Create delete/archive routes
- [ ] Add delete buttons to UI (admin only)
- [ ] Implement soft delete (archive) vs hard delete
- [ ] Create "view archived" page for admins

**Routes:**
```python
@app.route('/interaction/<id>/archive', methods=['POST'])
@requires_role('admin')
def archive_interaction(id):
    """Soft delete (archive) an interaction."""
    pass

@app.route('/interaction/<id>/delete', methods=['POST'])
@requires_role('admin')
def delete_interaction(id):
    """Hard delete an interaction (requires confirmation)."""
    pass

@app.route('/tool/<id>/archive', methods=['POST'])
@requires_role('admin')
def archive_tool(id):
    """Archive a tool."""
    pass
```

**Files to Modify:**
- Add `is_archived` field to models
- Create archive/delete routes
- Update list views to filter archived items
- Add admin view to see archived items

**Estimated Time:** 2 days

### 3.2 Create Admin Dashboard
**Tasks:**
- [ ] Build admin homepage with statistics
- [ ] Show pending actions (discoveries, flags, etc.)
- [ ] Display recent activity log
- [ ] Add quick links to admin functions

**Dashboard Components:**
- System statistics
- Pending approvals count
- Recent activity feed
- Data quality metrics
- User activity logs

**Files to Create:**
- `templates/admin/dashboard.html`
- `@app.route('/admin')` - Admin homepage

**Estimated Time:** 2 days

### 3.3 Add Bulk Operations
**Tasks:**
- [ ] Add checkboxes to interaction/tool lists
- [ ] Implement "Select All" functionality
- [ ] Create bulk delete/archive/approve actions
- [ ] Add bulk edit capabilities

**Estimated Time:** 1 day

### Deliverables:
- ✅ Delete and archive functionality
- ✅ Admin dashboard with overview
- ✅ Bulk operations for efficiency

---

## Phase 4: Discovery Queue Integration (Week 4-5)

**Priority: MEDIUM** - Automated discovery

### 4.1 Add Discovery Queue Tables
**Tasks:**
- [ ] Add discovery queue tables to database
- [ ] Create DiscoveryQueueItem model in streamlined_app.py
- [ ] Run database migration
- [ ] Add indexes for performance

**Migration:**
```python
# migrations/add_discovery_queue.py
def upgrade():
    op.create_table('discovery_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        # ... (all fields from docs/DISCOVERY_SYSTEM_ARCHITECTURE.md)
    )
    op.create_index('idx_discovery_status', 'discovery_queue', ['status'])
```

**Estimated Time:** 1 day

### 4.2 Create Discovery Review UI
**Tasks:**
- [ ] Create discovery queue list page
- [ ] Build discovery review card component
- [ ] Add approve/reject/edit actions
- [ ] Implement filtering and sorting

**Routes:**
```python
@app.route('/admin/discoveries')
@requires_role('editor')
def list_discoveries():
    """Show pending discoveries."""
    pass

@app.route('/admin/discoveries/<id>')
@requires_role('editor')
def review_discovery(id):
    """Review a single discovery."""
    pass

@app.route('/admin/discoveries/<id>/approve', methods=['POST'])
@requires_role('admin')
def approve_discovery(id):
    """Approve and import discovery."""
    pass
```

**Files to Create:**
- `templates/admin/discoveries.html` - Queue list
- `templates/admin/discovery_review.html` - Review page
- Discovery management routes

**Estimated Time:** 3 days

### 4.3 Implement Manual Discovery Entry
**Tasks:**
- [ ] Create "Submit Discovery" form
- [ ] Allow users to suggest tools/interactions
- [ ] Auto-add to discovery queue with 'user_submission' source
- [ ] Send to admin approval queue

**Estimated Time:** 2 days

### Deliverables:
- ✅ Discovery queue database tables
- ✅ Manual discovery submission
- ✅ Admin review interface

---

## Phase 5: Automated Discovery (Week 6-7)

**Priority: MEDIUM** - Scale discovery

### 5.1 Implement Core Watchers
**Tasks:**
- [ ] Complete RSS watcher implementation
- [ ] Complete GitHub watcher implementation
- [ ] Add configuration for API keys
- [ ] Create CLI command to run watchers manually

**CLI Commands:**
```bash
# Run all watchers
python manage.py discover --all

# Run specific watcher
python manage.py discover --source github

# Dry run (don't save to queue)
python manage.py discover --dry-run
```

**Files to Complete:**
- `discovery/watchers.py` - Already created
- `discovery/coordinator.py` - Needs creation
- `manage.py` - Add discovery commands

**Estimated Time:** 4 days

### 5.2 Add Enrichment Pipeline
**Tasks:**
- [ ] Implement basic enrichment (validation, normalization)
- [ ] Add Claude integration for AI enrichment
- [ ] Create confidence scoring algorithm
- [ ] Implement auto-approval threshold

**Files to Create:**
- `discovery/enrichment.py`
- `discovery/claude_agent.py`
- Configure ANTHROPIC_API_KEY

**Estimated Time:** 3 days

### Deliverables:
- ✅ Working RSS and GitHub watchers
- ✅ Basic enrichment pipeline
- ✅ Manual CLI execution

---

## Phase 6: Scheduling & Automation (Week 8)

**Priority: LOW** - Full automation

### 6.1 Setup Celery for Task Scheduling
**Tasks:**
- [ ] Install Celery and Redis
- [ ] Configure Celery tasks
- [ ] Create periodic tasks
- [ ] Setup monitoring

**Configuration:**
```python
# celery_config.py
CELERY_BEAT_SCHEDULE = {
    'run-discovery-watchers': {
        'task': 'tasks.run_discovery_cycle',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
    'process-enrichment-queue': {
        'task': 'tasks.process_enrichment',
        'schedule': crontab(minute='*/30'),  # Every 30 min
    },
}
```

**Estimated Time:** 3 days

### 6.2 Add Monitoring & Alerts
**Tasks:**
- [ ] Add Prometheus metrics
- [ ] Create health check endpoint
- [ ] Setup error alerting
- [ ] Create discovery statistics dashboard

**Estimated Time:** 2 days

### Deliverables:
- ✅ Automated discovery runs
- ✅ Monitoring and alerts
- ✅ Production-ready system

---

## Phase 7: Data Quality Improvements (Week 9)

**Priority: HIGH** - Clean up existing data

### 7.1 Add Data Validation
**Tasks:**
- [ ] Create validation rules for tools
- [ ] Create validation rules for interactions
- [ ] Add URL validation (check if URLs are alive)
- [ ] Flag incomplete/suspicious data

**Validation Rules:**
- Tool name required and unique
- URL format validation
- Check for duplicate interactions
- Description minimum length
- Stage must be valid MaLDReTH stage

**Estimated Time:** 2 days

### 7.2 Implement Data Quality Dashboard
**Tasks:**
- [ ] Create data quality metrics
- [ ] Show completeness scores
- [ ] Identify duplicates
- [ ] List items needing attention

**Metrics:**
- % tools with descriptions
- % tools with URLs
- % tools with open source status
- Average interaction detail length
- Duplicate detection

**Files to Create:**
- `templates/admin/data_quality.html`
- `@app.route('/admin/data-quality')`

**Estimated Time:** 2 days

### 7.3 Batch Update Tools
**Tasks:**
- [ ] Create script to re-run tool enrichment
- [ ] Update existing tools with enriched data
- [ ] Fill missing fields from external sources
- [ ] Document data sources

**Estimated Time:** 1 day

### Deliverables:
- ✅ Data validation rules
- ✅ Quality metrics dashboard
- ✅ Improved data completeness

---

## Phase 8: Enhanced Database Schema (Ongoing)

**Priority: MEDIUM** - Better data model

### 8.1 Extend Tool Model
**Current limitations:**
- No license field
- No github_url field
- No notes field
- No created_via field
- category_id and stage_id are required (too restrictive)

**Proposed New Fields:**
```python
class ExemplarTool(db.Model):
    # Existing fields...

    # New fields for enrichment
    license = db.Column(db.String(100))
    github_url = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_via = db.Column(db.String(100))  # 'UI', 'CSV Import', 'Discovery System'

    # Make these nullable for CSV imports
    stage_id = db.Column(db.Integer, db.ForeignKey('maldreth_stages.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.id'), nullable=True)

    # Additional metadata
    tags = db.Column(db.JSON)  # Array of tags
    alternative_names = db.Column(db.JSON)  # Array of alternative names
    is_archived = db.Column(db.Boolean, default=False)

    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
```

**Migration Required:** Yes - Alembic migration

**Estimated Time:** 1 day

### 8.2 Add Audit Logging
**Tasks:**
- [ ] Create audit_log table
- [ ] Log all create/update/delete operations
- [ ] Track who made changes
- [ ] Display audit log in admin interface

**Schema:**
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'create', 'update', 'delete', 'archive'
    user_id INTEGER REFERENCES users(id),
    changes JSONB,  -- Before/after values
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Estimated Time:** 2 days

### Deliverables:
- ✅ Extended tool model with all fields
- ✅ Flexible schema for imports
- ✅ Complete audit trail

---

## Phase 9: Documentation & Training (Week 10)

**Priority: MEDIUM** - User enablement

### 9.1 Update User Documentation
**Tasks:**
- [ ] Update README with new features
- [ ] Create admin user guide
- [ ] Document discovery system
- [ ] Create troubleshooting guide

**Estimated Time:** 2 days

### 9.2 Create Video Tutorials
**Tasks:**
- [ ] Screen recording: How to add interactions
- [ ] Screen recording: CSV upload process
- [ ] Screen recording: Admin curation workflow
- [ ] Screen recording: Discovery review

**Estimated Time:** 2 days

### 9.3 API Documentation
**Tasks:**
- [ ] Document all API endpoints
- [ ] Add OpenAPI/Swagger spec
- [ ] Create API examples
- [ ] Document authentication

**Estimated Time:** 1 day

### Deliverables:
- ✅ Comprehensive documentation
- ✅ Video tutorials
- ✅ API documentation

---

## Phase 10: Testing & Deployment (Week 11)

**Priority: HIGH** - Production readiness

### 10.1 Automated Testing
**Tasks:**
- [ ] Write unit tests for models
- [ ] Write integration tests for routes
- [ ] Add CSV import tests
- [ ] Test discovery system
- [ ] Test authentication and authorization

**Framework:** pytest + Flask-Testing

**Estimated Time:** 4 days

### 10.2 Production Deployment
**Tasks:**
- [ ] Setup production database
- [ ] Configure environment variables
- [ ] Deploy to Heroku/AWS
- [ ] Setup CI/CD pipeline
- [ ] Configure monitoring

**Estimated Time:** 2 days

### 10.3 Data Migration
**Tasks:**
- [ ] Backup production database
- [ ] Run all migrations
- [ ] Import enriched catalogs
- [ ] Validate data integrity
- [ ] Create admin users

**Estimated Time:** 1 day

### Deliverables:
- ✅ Automated test suite
- ✅ Production deployment
- ✅ Migrated data

---

## Dependencies & Prerequisites

### Required Software
- Python 3.11+
- PostgreSQL 13+
- Redis (for Celery)
- Git

### Python Packages to Install
```bash
# Authentication
pip install Flask-Login bcrypt

# Task queue
pip install celery redis

# Database migrations
pip install alembic

# API clients
pip install feedparser requests anthropic

# Web scraping (Phase 5+)
pip install scrapy beautifulsoup4

# Testing
pip install pytest pytest-flask

# Monitoring
pip install prometheus-client
```

### Environment Variables
```bash
# Authentication
SECRET_KEY=your-secret-key
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://...

# Claude API
ANTHROPIC_API_KEY=sk-...

# GitHub API
GITHUB_TOKEN=ghp_...

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0

# Admin
ADMIN_EMAIL=admin@example.com
```

---

## Risk Management

### High Risk Items
1. **Database migrations** - Could break existing data
   - Mitigation: Test on staging first, backup before migration

2. **Authentication security** - Vulnerable to attacks
   - Mitigation: Use Flask-Login best practices, rate limiting

3. **API rate limits** - GitHub, Claude APIs have limits
   - Mitigation: Implement backoff, caching, request throttling

4. **Data quality** - Bad discoveries could pollute catalog
   - Mitigation: Human review, confidence thresholds, rollback capability

### Medium Risk Items
1. **Celery complexity** - Adds operational overhead
   - Mitigation: Start with manual CLI execution, add Celery later

2. **User adoption** - Admin features may not be used
   - Mitigation: Good UX, training, documentation

---

## Success Metrics

### Phase 1-3 (Weeks 1-3)
- ✅ CSV uploads working without errors
- ✅ Admin role implemented
- ✅ Delete functionality works
- ✅ 90% tool CSV import success rate

### Phase 4-6 (Weeks 4-8)
- ✅ Discovery queue operational
- ✅ 10+ tools discovered per week
- ✅ Human review < 1 hour per week
- ✅ 80% approval rate

### Phase 7-10 (Weeks 9-11)
- ✅ 95%+ data completeness
- ✅ All tests passing
- ✅ Production deployment stable
- ✅ Zero data loss incidents

---

## Budget Estimate

### Development Time
- **Phase 1-3 (Critical)**: 3 weeks × 40 hours = 120 hours
- **Phase 4-6 (Core)**: 4 weeks × 40 hours = 160 hours
- **Phase 7-10 (Polish)**: 4 weeks × 40 hours = 160 hours
- **Total**: 440 hours (~11 weeks full-time)

### Infrastructure Costs (Annual)
- Heroku Hobby ($7/mo × 12) = $84
- Redis Cloud Basic ($5/mo × 12) = $60
- PostgreSQL Standard ($50/mo × 12) = $600
- Claude API (~$50/mo × 12) = $600
- GitHub Actions (Free tier)
- **Total**: ~$1,350/year

---

## Prioritization Recommendation

### Must Have (Launch Blocker)
1. ✅ Fix CSV imports (Phase 1)
2. ✅ Admin role (Phase 2)
3. ✅ Delete functionality (Phase 3)
4. ✅ Extended tool model (Phase 8.1)

### Should Have (Launch Soon)
5. ✅ Discovery queue UI (Phase 4)
6. ✅ Manual discovery submission (Phase 4.3)
7. ✅ Data quality dashboard (Phase 7.2)

### Nice to Have (Post-Launch)
8. ✅ Automated watchers (Phase 5)
9. ✅ Celery scheduling (Phase 6)
10. ✅ Advanced monitoring (Phase 6.2)

---

## Next Immediate Steps

### This Week
1. **Fix tool model** - Add license, github_url, notes fields
2. **Fix CSV imports** - Add missing import, test both uploads
3. **Add navigation** - Link to tool CSV upload
4. **Test with real data** - Upload enriched catalogs

### Next Week
5. **Implement authentication** - Flask-Login setup
6. **Create admin role** - Protect sensitive operations
7. **Add delete buttons** - Archive/delete interactions and tools

---

**Document Version**: 1.0
**Last Updated**: October 2025
**Owner**: MaLDReTH II Working Group
**Status**: Ready for Implementation
**Next Review**: End of Phase 1
