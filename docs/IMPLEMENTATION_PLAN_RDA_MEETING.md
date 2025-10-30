# PRISM Implementation Plan - RDA MaLDReTH II Meeting Follow-up

**Date:** October 30, 2025
**Status:** Draft Implementation Plan
**Meeting Reference:** RDA MaLDReTH II WG Co-chairs Meeting

---

## Executive Summary

Following the successful RDA session presentation and co-chairs meeting, this plan outlines technical and strategic implementations to address key feedback and accelerate PRISM development through a hybrid data collection approach.

**Key Priorities:**
1. Add alpha status warnings and public visibility
2. Create feedback collection mechanism
3. Implement hybrid data collection workflow
4. Improve cross-linking with MaLDReTH I
5. Support asynchronous and group exercise participation

---

## Phase 1: Immediate Website Updates (Week 1)

### 1.1 Alpha Status Banner
**Priority:** HIGH
**Effort:** 2-3 hours
**Owner:** Development Team

**Requirements:**
- Add prominent banner to all pages indicating alpha/development status
- Include version information and development stage
- Provide context about ongoing development
- Link to feedback mechanism

**Technical Implementation:**
```html
<!-- Add to base template header -->
<div class="alert alert-warning alert-dismissible fade show mb-0" role="alert">
  <div class="container">
    <i class="fas fa-exclamation-triangle me-2"></i>
    <strong>Alpha Version:</strong> PRISM is in active development.
    Data structures and features may change.
    <a href="{{ url_for('feedback') }}" class="alert-link">Share feedback</a>
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  </div>
</div>
```

**Success Criteria:**
- [ ] Banner visible on all public pages
- [ ] Dismissible but persistent across sessions
- [ ] Clear messaging about alpha status
- [ ] Link to feedback collection

---

### 1.2 Feedback Collection Page
**Priority:** HIGH
**Effort:** 4-6 hours
**Owner:** Development Team
**Timeline:** 1-2 week collection window

**Requirements:**
- Simple form for collecting structured feedback
- Categories: Usability, Data Quality, Features, Documentation, Other
- Optional contact information
- Export feedback to CSV for review
- Thank you message with expected response time

**Technical Implementation:**

**New Route (`/feedback`):**
```python
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Collect user feedback on PRISM alpha."""
    if request.method == 'POST':
        # Store feedback in database or CSV
        # Send notification email
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))

    return render_template('feedback.html')
```

**Database Model:**
```python
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))  # Usability, Data, Features, etc.
    feedback_text = db.Column(db.Text, nullable=False)
    page_url = db.Column(db.String(500))  # Page where feedback originated
    contact_name = db.Column(db.String(200))  # Optional
    contact_email = db.Column(db.String(200))  # Optional
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # new, reviewed, addressed
```

**Success Criteria:**
- [ ] Feedback form accessible from banner and Help menu
- [ ] Stores feedback with metadata (page, timestamp)
- [ ] Optional contact information
- [ ] Admin view to review feedback
- [ ] CSV export capability

---

## Phase 2: Hybrid Data Collection Workflow (Week 2-3)

### 2.1 Google Spreadsheet Template
**Priority:** HIGH
**Effort:** 3-4 hours
**Owner:** Development + WG Co-chairs

**Requirements:**
- Create template with simplified criteria: "technically possible and logically desirable"
- Columns aligned with PRISM CSV import format
- Clear instructions and examples
- Validation rules where possible
- Reference to GitHub crawl results

**Template Structure:**
```
Columns:
1. Source Tool (required)
2. Target Tool (required)
3. Interaction Type (dropdown)
4. Lifecycle Stage (dropdown)
5. Description (required)
6. Technically Possible? (Yes/No/Unknown)
7. Logically Desirable? (Yes/No/Unknown)
8. Technical Details (optional)
9. Examples/Evidence (optional)
10. GitHub Reference (optional)
11. Submitted By (optional)
12. Notes
```

**Instruction Tabs:**
1. **How to Use** - Step-by-step guide
2. **Interaction Types** - Definitions and examples
3. **Lifecycle Stages** - MaLDReTH II stage descriptions
4. **Tool Names** - Valid tool list from PRISM
5. **Examples** - 10-15 good examples

**Success Criteria:**
- [ ] Template shared with WG
- [ ] Instructions clear for asynchronous participation
- [ ] Validation prevents common errors
- [ ] Easy to import into PRISM
- [ ] Reference materials included

---

### 2.2 Enhanced CSV Import with Validation Reports
**Priority:** MEDIUM
**Effort:** 4-5 hours
**Owner:** Development Team

**Requirements:**
- Add pre-import validation with detailed reporting
- Check for "technically possible" and "logically desirable" flags
- Generate quality score for imports
- Provide suggestions for improvement
- Track import source (async submission vs. group exercise)

**Enhanced Import Flow:**
```python
def validate_import_quality(csv_data):
    """
    Validate CSV import and provide quality report.

    Returns:
        dict: {
            'total_rows': int,
            'valid_rows': int,
            'warnings': list,
            'errors': list,
            'quality_score': float,
            'suggestions': list
        }
    """
    report = {
        'total_rows': len(csv_data),
        'valid_rows': 0,
        'warnings': [],
        'errors': [],
        'suggestions': []
    }

    for row in csv_data:
        # Check required fields
        # Validate technical feasibility flags
        # Check for evidence/examples
        # Score completeness

    report['quality_score'] = (report['valid_rows'] / report['total_rows']) * 100

    return report
```

**Success Criteria:**
- [ ] Pre-import validation report
- [ ] Quality scoring system
- [ ] Actionable suggestions
- [ ] Track import metadata
- [ ] Support batch review before commit

---

### 2.3 Group Exercise Support Features
**Priority:** MEDIUM
**Effort:** 6-8 hours
**Owner:** Development Team

**Requirements:**
- Session-based collaborative editing
- Real-time validation feedback
- Bulk review interface
- Export session results
- Assign interactions to reviewers

**New Features:**

**1. Batch Review Interface (`/review/batch/<session_id>`)**
- Display all pending interactions from a session
- Quick approve/reject/edit actions
- Filter by quality score
- Assign to reviewers
- Export decisions

**2. Interaction Session Model:**
```python
class InteractionSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))  # "Async Round 1", "Group Exercise Oct 2025"
    session_type = db.Column(db.String(50))  # async, group_exercise
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))  # active, review, completed
    total_submissions = db.Column(db.Integer, default=0)
    approved_count = db.Column(db.Integer, default=0)
```

**Success Criteria:**
- [ ] Support multiple concurrent sessions
- [ ] Batch operations for efficiency
- [ ] Quality filtering
- [ ] Session summary reports
- [ ] Easy export to spreadsheet

---

## Phase 3: Website Integration & Cross-linking (Week 3-4)

### 3.1 Add PRISM to MaLDReTH Website
**Priority:** HIGH
**Effort:** Coordination with web team
**Owner:** WG Co-chairs + Web Admin

**Requirements:**
- Add PRISM link to main MaLDReTH II page
- Include alpha warning in description
- Link to user guide and documentation
- Highlight stakeholder interest from RDA session

**Suggested Website Updates:**

**Navigation:**
```
MaLDReTH II > Tools & Resources > PRISM (Alpha)
```

**Description:**
```
PRISM (Platform for Research Infrastructure Synergy Mapping) - ALPHA
An interactive tool for mapping and visualizing digital research tool
interactions across the research data lifecycle.

⚠️ Currently in alpha development - data structures may change
📚 User Guide | 💬 Feedback | 🎥 RDA Presentation
```

**Success Criteria:**
- [ ] PRISM visible on MaLDReTH website
- [ ] Clear alpha status indicators
- [ ] Links to documentation
- [ ] Contact/feedback mechanism

---

### 3.2 Improve MaLDReTH I/II Cross-linking
**Priority:** MEDIUM
**Effort:** 2-3 hours
**Owner:** Development + Documentation Team

**Current Issue:**
- Different acronyms cause findability problems
- Users may not realize MaLDReTH II is continuation

**Requirements:**
- Add prominent link to original MaLDReTH from PRISM
- Explain relationship between MaLDReTH I and II
- Cross-reference in documentation
- Include timeline/history

**Implementation:**

**Add to About Page:**
```html
<section class="maldreth-lineage">
  <h3>MaLDReTH Lineage</h3>
  <div class="timeline">
    <div class="timeline-item">
      <h4>MaLDReTH I (2020-2023)</h4>
      <p>Original mapping of digital research tools landscape</p>
      <a href="[original URL]">View MaLDReTH I Resources</a>
    </div>
    <div class="timeline-item">
      <h4>MaLDReTH II (2023-Present)</h4>
      <p>Harmonized approach with enhanced categorization and interaction mapping</p>
      <a href="{{ url_for('index') }}">PRISM Platform</a>
    </div>
  </div>
</section>
```

**Footer Update:**
```html
<p class="small">
  Part of the <a href="[MaLDReTH II URL]">MaLDReTH II</a> initiative,
  continuing work from <a href="[MaLDReTH I URL]">MaLDReTH I</a>
</p>
```

**Success Criteria:**
- [ ] Clear explanation of MaLDReTH evolution
- [ ] Links to both MaLDReTH I and II resources
- [ ] Timeline/history visible
- [ ] Cross-references in documentation

---

### 3.3 RDA Session Recording Integration
**Priority:** LOW (waiting on RDA)
**Effort:** 1 hour
**Owner:** Development Team

**Requirements:**
- Add section for RDA session recordings
- Link to YouTube when available (few weeks delay)
- Highlight Oslava Tikhonov's Crossref/Google AI presentation
- Include presentation slides and materials

**Implementation Location:**
- About page
- Resources section
- Welcome modal (update)

**Success Criteria:**
- [ ] Placeholder prepared for recording links
- [ ] Update process documented
- [ ] Nina to provide links when available

---

## Phase 4: Data Population Strategy (Ongoing)

### 4.1 Initial Asynchronous Round
**Priority:** HIGH
**Timeline:** 2-3 weeks
**Owner:** WG Co-chairs

**Process:**
1. Distribute Google spreadsheet template to working group
2. Set clear deadline (2 weeks from distribution)
3. Provide GitHub crawl results as reference
4. Weekly reminder emails
5. Office hours for questions

**Target:**
- 50-100 high-quality interactions
- Establish process and criteria
- Identify common challenges
- Refine template based on feedback

**Success Criteria:**
- [ ] Template distributed
- [ ] Support materials provided
- [ ] Clear deadline communicated
- [ ] Minimum 50 submissions received
- [ ] Process documented for next round

---

### 4.2 Group Exercise Planning
**Priority:** MEDIUM
**Timeline:** After async round completion
**Owner:** WG Co-chairs

**Format Options:**
1. **Virtual Workshop (2-3 hours)**
   - Breakout groups by lifecycle stage
   - Real-time collaboration
   - PRISM interface demo
   - Immediate import and review

2. **Hybrid In-person/Virtual**
   - Combine with conference or meeting
   - Hands-on PRISM training
   - Interactive data entry
   - Group validation

**Requirements:**
- Facilitator guide
- Participant instructions
- Technical setup checklist
- Backup plans for technical issues

**Success Criteria:**
- [ ] Format selected
- [ ] Date scheduled
- [ ] Materials prepared
- [ ] Participants confirmed
- [ ] Technical testing complete

---

## Phase 5: Dutch Open Science Festival Insights (Future)

### 5.1 Interoperability Focus Areas
**Priority:** LOW (future consideration)
**Owner:** Strategic Planning

**Key Takeaways:**
- Three Digital Compensation Centers with dedicated funding
- Major shift toward interoperability
- Interoperability leads appointed per thematic group
- Potential collaboration opportunities

**Potential PRISM Enhancements:**
- Map tool interoperability capabilities
- Track standards compliance (e.g., FAIR, RO-Crate)
- Connect with Dutch DCC initiatives
- Highlight interoperability in interaction types

**Success Criteria:**
- [ ] Monitor Dutch DCC developments
- [ ] Identify collaboration opportunities
- [ ] Consider interoperability metrics
- [ ] Connect with Dutch leads

---

## Technical Implementation Priorities

### Immediate (Next 7 days)
1. ✅ User Guide completed (DONE)
2. 🔲 Alpha status banner
3. 🔲 Feedback collection page
4. 🔲 Google spreadsheet template

### Short-term (Weeks 2-3)
1. 🔲 Enhanced CSV validation
2. 🔲 Batch review interface
3. 🔲 Website cross-linking
4. 🔲 Async data collection round

### Medium-term (Weeks 4-6)
1. 🔲 Group exercise features
2. 🔲 RDA recording integration
3. 🔲 Session management tools
4. 🔲 Quality scoring system

### Long-term (2-3 months)
1. 🔲 Interoperability tracking
2. 🔲 Advanced analytics
3. 🔲 API enhancements
4. 🔲 Dutch DCC collaboration exploration

---

## Success Metrics

### Engagement Metrics
- Number of async submissions
- Group exercise participation rate
- Feedback submissions
- Website traffic to PRISM
- User guide page views

### Data Quality Metrics
- Percentage of submissions with evidence
- Average completeness score
- Technical feasibility coverage
- Logical desirability coverage
- Duplicate rate reduction

### Community Metrics
- Active contributors count
- Repeat contributors
- Geographic distribution
- Institutional diversity
- Feedback response rate

---

## Resource Requirements

### Development Time
- Phase 1: 8-10 hours
- Phase 2: 15-20 hours
- Phase 3: 5-8 hours
- Phase 4: Coordination time (WG co-chairs)

### Infrastructure
- No additional infrastructure required
- Existing Heroku deployment sufficient
- Google Workspace for spreadsheets
- Email notifications (existing setup)

### Coordination
- WG co-chairs: Template creation, async round management
- Web admin: Website updates
- RDA liaison: Recording links
- Development: Technical implementation

---

## Risk Management

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Import errors with spreadsheet data | HIGH | Pre-validation, clear templates, examples |
| Performance with bulk imports | MEDIUM | Batch processing, progress indicators |
| User confusion with alpha status | MEDIUM | Clear messaging, documentation, support |

### Process Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Low async participation | HIGH | Clear deadlines, reminders, office hours |
| Data quality issues | MEDIUM | Validation tools, review process |
| Timeline delays | LOW | Phased approach, flexible scheduling |

### Community Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Contributor fatigue | MEDIUM | Simplified criteria, recognition |
| Duplicate efforts | LOW | Clear coordination, session management |
| Inconsistent standards | MEDIUM | Templates, examples, validation |

---

## Next Steps & Action Items

### Immediate Actions (This Week)
- [ ] Review and approve this implementation plan
- [ ] Assign owners for Phase 1 tasks
- [ ] Create alpha status banner
- [ ] Build feedback collection page
- [ ] Draft Google spreadsheet template

### Coordination Needed
- [ ] Schedule demo meeting for data collection approach walkthrough
- [ ] Confirm MaLDReTH II maintenance status with RDA
- [ ] Coordinate website updates with web admin
- [ ] Plan async round timeline with co-chairs

### Communication
- [ ] Announce PRISM alpha availability to working group
- [ ] Share implementation plan with co-chairs
- [ ] Prepare announcement for website
- [ ] Draft async round invitation email

---

## Document Control

**Version:** 1.0
**Date:** October 30, 2025
**Author:** Development Team
**Reviewers:** WG Co-chairs
**Next Review:** November 6, 2025

**Change Log:**
- 2025-10-30: Initial plan created based on RDA meeting outcomes

---

## Appendices

### Appendix A: Simplified Criteria Framework

**"Technically Possible"** - Can these tools actually integrate?
- API availability
- Data format compatibility
- Technical documentation exists
- Known implementations (even if rare)
- No fundamental technical blockers

**"Logically Desirable"** - Should these tools integrate?
- Serves common research workflow
- Enhances research outcomes
- Reduces manual effort
- Improves data quality/FAIR compliance
- Addresses real user need

### Appendix B: GitHub Crawl Reference
*To be populated with links to GitHub crawl results when available*

### Appendix C: Contact Information
- Development Team: [contact]
- WG Co-chairs: halle.burns@princeton.edu, nina@codata.org, rmacneil@researchspace.com, maria.praetzellis@ucop.edu
- Feedback: [feedback form URL when created]

---

**End of Implementation Plan**
