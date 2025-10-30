# PRISM User Guide: Adding and Curating Interactions

**PRISM** - Platform for Research Infrastructure Synergy Mapping

This guide provides step-by-step instructions for contributing and maintaining tool interaction data in PRISM.

---

## Table of Contents

1. [Understanding Tool Interactions](#1-understanding-tool-interactions)
2. [Before You Start](#2-before-you-start)
3. [Adding Interactions via Web Form](#3-adding-interactions-via-web-form)
4. [Bulk Import via CSV](#4-bulk-import-via-csv)
5. [Curating Existing Interactions](#5-curating-existing-interactions)
6. [Best Practices](#6-best-practices)
7. [Common Scenarios](#7-common-scenarios)
8. [Quality Guidelines](#8-quality-guidelines)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Understanding Tool Interactions

### What is a Tool Interaction?

A **tool interaction** in PRISM represents a connection or integration between two research tools in the digital research ecosystem. Interactions enable data flow, functionality enhancement, or workflow integration across the research data lifecycle.

### Components of an Interaction

Every interaction consists of:

- **Source Tool**: The tool that initiates or provides data/functionality
- **Target Tool**: The tool that receives data/functionality
- **Interaction Type**: How the tools connect (API, data exchange, plugin, etc.)
- **Lifecycle Stage**: Which stage of the research data lifecycle this interaction supports
- **Description**: What the interaction does and why it matters

### Example

> **GitHub** → **Zenodo** (Source → Target)
> - **Type**: Data Exchange
> - **Stage**: PRESERVE
> - **Description**: "GitHub repositories are automatically archived to Zenodo with DOI assignment, creating permanent records of research software."

---

## 2. Before You Start

### Prerequisites

✅ **Account Access**: Access to the PRISM web interface at [https://mal2-data-survey-cb27f6674f20.herokuapp.com/](https://mal2-data-survey-cb27f6674f20.herokuapp.com/)

✅ **Knowledge**: Familiarity with the tools you're documenting and how they interact

✅ **Reference Materials**:
   - Tool documentation or user guides
   - Examples of the interaction in action
   - Technical specifications (API docs, integration guides)

### Familiarize Yourself

Before adding interactions, explore:

1. **Tool Catalog** (`/tools`): View all 267+ research tools in PRISM
2. **Glossary** (`/glossary`): Understand terminology and interaction types
3. **Existing Interactions** (`/interactions`): See examples of well-documented interactions
4. **Visualizations** (`/radial-visualization`): Understand how interactions are displayed

---

## 3. Adding Interactions via Web Form

The web form is ideal for adding single, well-researched interactions with detailed information.

### Step-by-Step Guide

#### Step 1: Navigate to Add Interaction Page

1. Go to PRISM homepage
2. Click **"Add Interaction"** in the navigation menu
3. Or navigate directly to `/interaction/add`

#### Step 2: Select Tools

**Source Tool:**
- Select the tool that **initiates** the interaction
- Use the searchable dropdown (type to filter)
- Each tool shows its lifecycle stage in parentheses

**Target Tool:**
- Select the tool that **receives** data/functionality
- Cannot be the same as source tool
- Consider the direction of data/functionality flow

**💡 Tip**: The order matters! Think about causality:
- GitHub → Zenodo (GitHub pushes to Zenodo) ✅
- Zenodo → GitHub (backwards) ❌

#### Step 3: Define Interaction Details

**Interaction Type** (required) - Choose from:
- **API Integration**: Direct programmatic connection via APIs
- **Data Exchange**: Structured data transfer between tools
- **Metadata Exchange**: Sharing of descriptive information
- **File Format Conversion**: Transforming data between formats
- **Workflow Integration**: Tools working together in a process
- **Plugin/Extension**: One tool extends another's functionality
- **Direct Database Connection**: Database-level integration
- **Web Service**: Web-based service integration
- **Command Line Interface**: CLI-based interaction
- **Import/Export**: Manual or semi-automated data transfer
- **Other**: Specify in description if none fit

**Lifecycle Stage** (required) - Select the primary stage:
- **PLAN**: Research planning and proposal development
- **COLLECT**: Data collection and generation
- **PROCESS**: Data processing and cleaning
- **ANALYSE**: Data analysis and interpretation
- **PRESERVE**: Long-term data preservation
- **SHARE**: Data sharing and dissemination
- **PUBLISH**: Publication and formal release
- **DISCOVER**: Data discovery and search
- **REUSE**: Data reuse in new contexts
- **INTEGRATE**: Cross-dataset integration
- **MANAGE**: Data management and governance
- **ASSESS**: Quality assessment and evaluation

**Description** (required):
- 1-3 sentences explaining what happens and why it's useful
- Focus on user benefits, not just technical details
- Example: "Zenodo automatically links publications and datasets to ORCID profiles, enabling comprehensive research output tracking and attribution across the scholarly ecosystem."

#### Step 4: Add Technical Details (Optional but Recommended)

**Technical Details:**
- Implementation specifics (REST API, OAuth 2.0, etc.)
- Technical requirements or dependencies
- Example: "REST API integration with ORCID authentication, DOI-based linking"

**Benefits:**
- Advantages for researchers or workflows
- Efficiency gains, cost savings, or quality improvements
- Example: "Enhanced researcher visibility, automated attribution, improved discoverability"

**Challenges:**
- Known limitations or difficulties
- Prerequisites or barriers to adoption
- Example: "API rate limits, authentication complexity, metadata inconsistencies"

**Examples:**
- Real-world use cases or scenarios
- Specific implementations or deployments
- Example: "Research publications automatically linked to ORCID profiles upon Zenodo deposit"

#### Step 5: Add Contact Information (Optional)

**Contact Person**: Name of subject matter expert

**Organization**: Institution or company

**Email**: Contact email for follow-up questions

**💡 Tip**: Providing contact information helps with verification and future updates

#### Step 6: Set Metadata

**Priority**:
- **High**: Critical infrastructure interactions
- **Medium**: Commonly used integrations
- **Low**: Niche or experimental connections

**Complexity**:
- **Simple**: Works out-of-the-box, minimal configuration
- **Moderate**: Some technical setup required
- **Complex**: Significant technical expertise needed

**Status**:
- **Proposed**: Planned or conceptual
- **Pilot**: In testing or limited deployment
- **Implemented**: Fully operational and widely available
- **Deprecated**: No longer supported or recommended

**Submitted By**: Your name or identifier

#### Step 7: Review and Submit

1. Review all fields for accuracy
2. Check that source/target tools are in correct order
3. Click **"Add Interaction"**
4. You'll be redirected to the interaction list with a success message

### Form Features

- **Tooltips**: Hover over 🛈 icons for field-specific help
- **Glossary Links**: Click on terms to view detailed definitions
- **Auto-validation**: Required fields are marked and validated
- **Search**: Tool dropdowns support type-to-search

---

## 4. Bulk Import via CSV

CSV import is ideal for adding multiple interactions at once, especially when working from spreadsheets or external sources.

### Step 1: Prepare Your CSV File

#### Download Template

1. Navigate to `/upload/interactions/csv`
2. Click **"Download Current Data as Template"**
3. This provides the correct column structure

#### CSV Structure

**Required Columns:**
```
Source Tool, Target Tool, Interaction Type, Lifecycle Stage
```

**Optional Columns:**
```
Description, Technical Details, Benefits, Challenges, Examples,
Contact Person, Organization, Email, Priority, Complexity, Status, Submitted By
```

#### Example CSV Content

```csv
Source Tool,Target Tool,Interaction Type,Lifecycle Stage,Description,Priority,Status
GitHub,Zenodo,Data Exchange,PRESERVE,"GitHub repositories can be automatically archived to Zenodo with DOI assignment.",medium,implemented
DMPTool,RSpace,API Integration,PLAN,"DMPTool integrates with RSpace through API-based connections for comprehensive data management planning.",high,pilot
REDCap,R,Data Exchange,ANALYSE,"REDCap provides direct export capabilities to R for statistical analysis.",high,implemented
```

### Step 2: Validate Your Data

Before uploading, verify:

✅ **Tool Names**: Must exactly match existing tools in PRISM
   - Check `/tools` or `/api/v1/tools` for valid tool names
   - Case-sensitive matching
   - Include spaces and special characters as shown

✅ **Interaction Types**: Must be from the predefined list
   - API Integration, Data Exchange, Metadata Exchange, etc.
   - See Section 3 for complete list

✅ **Lifecycle Stages**: Must match MaLDReTH stages
   - PLAN, COLLECT, PROCESS, ANALYSE, PRESERVE, SHARE, PUBLISH, DISCOVER, REUSE, INTEGRATE, MANAGE, ASSESS

✅ **CSV Format**:
   - UTF-8 encoding
   - Comma-separated (not semicolon or tab)
   - Quoted fields if they contain commas
   - First row must be header row

### Step 3: Upload CSV

1. Navigate to `/upload/interactions/csv`
2. Click **"Choose File"** or drag-and-drop
3. Click **"Upload and Process"**
4. Wait for validation and processing

### Step 4: Review Upload Results

The system will display:

✅ **Successfully Imported**: New interactions added to database

⚠️ **Duplicates Detected**: Interactions already exist (skipped)

❌ **Validation Errors**: Issues with tool names, types, or required fields

**Example Results Page:**
```
✓ Successfully imported 3 interactions
⚠ Skipped 1 duplicate
✗ 2 errors:
  - Row 5: Tool 'GitLab CE' not found in database
  - Row 7: Invalid lifecycle stage 'ARCHIVE' (must be one of: PLAN, COLLECT, ...)
```

### Step 5: Correct Errors and Retry

If errors occur:

1. Download the error report (if available)
2. Correct issues in your CSV file
3. Re-upload only the failed rows
4. Or add failed interactions manually via web form

### Duplicate Detection

PRISM automatically prevents duplicates based on:
- Source Tool + Target Tool + Interaction Type + Lifecycle Stage

If a duplicate is detected:
- The upload will skip that row
- Existing data is preserved
- Use the curation interface to update instead

---

## 5. Curating Existing Interactions

Curation involves reviewing, correcting, and enriching existing interaction data to maintain quality and completeness.

### When to Curate

- **Incomplete Data**: Missing technical details or examples
- **Outdated Information**: Status changes, deprecated integrations
- **Improved Understanding**: Better descriptions based on new knowledge
- **Error Correction**: Fix typos, wrong tools, or incorrect stages
- **Enrichment**: Add benefits, challenges, or contact information

### Step-by-Step Curation

#### Step 1: Find the Interaction

**Option A: Browse**
1. Navigate to `/interactions`
2. Use filters to narrow down (stage, type, status)
3. Click on an interaction to view details

**Option B: Search**
1. Use the search box on `/interactions`
2. Type tool names, keywords, or interaction types
3. Filter results using advanced options

**Option C: Direct URL**
- If you know the interaction ID: `/interaction/<id>/edit`

#### Step 2: Review Current Data

1. Read the full interaction record
2. Check for accuracy and completeness
3. Identify what needs updating

#### Step 3: Edit the Interaction

1. Click **"Edit"** button (✏️ icon)
2. You'll see the curation interface
3. All fields are pre-populated with current data

**Curation Mode Banner:**
> 🛈 You are editing interaction #42. Changes will update the existing record.

#### Step 4: Make Updates

**Core Fields:**
- Modify source/target tools if incorrect
- Update interaction type if better fit exists
- Adjust lifecycle stage if misclassified
- Improve description for clarity

**Enhancement Fields:**
- Add technical details from documentation
- Document benefits based on user feedback
- List known challenges or limitations
- Provide concrete examples of usage
- Update status (pilot → implemented, etc.)

**Contact Information:**
- Add or update subject matter experts
- Include organizational context
- Provide email for verification

**💡 Best Practice**: Add a note in the description about what you changed and why, if significant.

#### Step 5: Save Changes

1. Review all modifications
2. Click **"Save Changes"**
3. Changes are immediately live in PRISM
4. View the updated interaction to verify

### Bulk Curation

For multiple interactions requiring similar updates:

1. Export current data via CSV (`/export/interactions/csv`)
2. Edit in spreadsheet software
3. Delete all rows except those you're updating
4. Upload via CSV import
5. System will update existing records based on matching criteria

---

## 6. Best Practices

### Writing Quality Descriptions

✅ **DO:**
- Focus on what the interaction enables for researchers
- Use clear, concise language (1-3 sentences)
- Explain the "why" not just the "what"
- Include context about research workflows

❌ **DON'T:**
- Use overly technical jargon without explanation
- Write vague descriptions ("these tools work together")
- Include marketing language or superlatives
- Copy-paste from tool websites without context

**Example - Good:**
> "Jupyter notebooks can be containerized using Docker to ensure reproducible computational environments across different systems and platforms, enabling researchers to share analysis workflows that run identically regardless of local setup."

**Example - Poor:**
> "Jupyter and Docker work together. This is useful."

### Selecting the Right Lifecycle Stage

Consider where the interaction has **primary impact**:

- **COLLECT**: Data entry, sensor integration, lab instruments
- **ANALYSE**: Statistical analysis, visualization, computation
- **PRESERVE**: Long-term storage, archiving, repositories
- **PUBLISH**: Publishing platforms, DOI minting, article submission

**💡 Tip**: If an interaction spans multiple stages, choose the one where it provides the most value or is most commonly used.

### Choosing Interaction Types

**API Integration** vs **Data Exchange**:
- **API Integration**: Real-time, programmatic, bidirectional
- **Data Exchange**: Often batch-based, one-directional, file-based

**Plugin/Extension** vs **Workflow Integration**:
- **Plugin**: One tool becomes part of another's interface
- **Workflow**: Tools used sequentially in a process

**When in doubt**: Choose "Other" and explain clearly in the description

### Contact Information

**Include contacts when:**
- You have permission to share their information
- They are public points of contact for the integration
- They've contributed to documenting this interaction

**Omit contacts when:**
- No clear subject matter expert exists
- Contact information is confidential
- You're documenting based on public information only

---

## 7. Common Scenarios

### Scenario 1: Two-Way Integrations

**Question**: GitHub and Zenodo have bidirectional integration. Should I create two interactions?

**Answer**: Yes, create separate interactions if the directionality matters:
- GitHub → Zenodo (archiving repositories)
- Zenodo → GitHub (linking back to source code)

Each has different use cases and technical implementations.

### Scenario 2: One Tool, Multiple Targets

**Question**: ORCID connects to Zenodo, figshare, DataCite, and many others. How should I document this?

**Answer**: Create separate interactions for each connection:
- ORCID → Zenodo (authentication and profile linking)
- ORCID → figshare (researcher identification)
- ORCID → DataCite (persistent identifiers)

Each interaction may have different technical details and use cases.

### Scenario 3: Tool Not in Database

**Question**: I want to document an interaction, but one of the tools isn't in PRISM yet.

**Answer**:
1. Check `/tools` to confirm the tool is truly missing
2. Check for alternate tool names or spellings
3. Contact the PRISM administrators to request tool addition
4. For CSV imports, the validation will identify missing tools

### Scenario 4: Unsure About Technical Details

**Question**: I know the interaction exists but don't understand the technical implementation.

**Answer**:
1. Add the interaction with basic details (source, target, type, stage, description)
2. Leave technical fields blank or note "Implementation details needed"
3. Provide contact information of someone who might know
4. The community can help enrich later through curation

### Scenario 5: Experimental or Proposed Interactions

**Question**: Can I document interactions that are planned but not yet implemented?

**Answer**: Yes! Set the **Status** field appropriately:
- **Proposed**: Conceptual or planning phase
- **Pilot**: In testing or limited rollout
- **Implemented**: Fully operational

This helps track the evolution of the research infrastructure landscape.

### Scenario 6: Deprecated or Sunset Integrations

**Question**: Should I document interactions that no longer work?

**Answer**: Yes, for historical context:
1. Keep the interaction record
2. Set **Status** to **Deprecated**
3. Update description to note "No longer supported as of [date]"
4. Explain in challenges: "Service discontinued" or "Replaced by [new tool]"

This helps researchers understand ecosystem evolution.

---

## 8. Quality Guidelines

### Minimum Data Quality Standards

Every interaction should have:

✅ Correct source and target tools in proper order
✅ Appropriate interaction type selection
✅ Accurate lifecycle stage assignment
✅ Clear description (minimum 1 sentence)
✅ Appropriate status indicator

### Enhanced Data Quality (Recommended)

For high-quality, curated interactions:

✅ Technical details with implementation specifics
✅ Benefits clearly articulated
✅ Known challenges or limitations documented
✅ At least one concrete example provided
✅ Priority and complexity assessed
✅ Contact information for verification

### Red Flags to Avoid

❌ **Generic descriptions**: "Tool A and Tool B integrate"
❌ **Wrong directionality**: Source/target reversed
❌ **Incorrect stages**: Choosing ANALYSE for a preservation tool
❌ **Missing context**: Technical jargon without explanation
❌ **Duplicate entries**: Same interaction documented multiple times
❌ **Outdated status**: Marking deprecated integrations as "Implemented"

### Verification Tips

Before finalizing an interaction:

1. **Tool Documentation**: Check official docs to verify the interaction exists
2. **User Experience**: Have you or someone you know used this integration?
3. **Technical Accuracy**: Are the technical details correct?
4. **Current Status**: Is the integration still active and supported?
5. **Peer Review**: Have a colleague review complex or critical interactions

---

## 9. Troubleshooting

### CSV Upload Issues

**Problem**: "Tool 'X' not found in database"
- **Solution**: Check exact spelling at `/tools` or use `/api/v1/tools` for valid names
- **Solution**: Tool may need to be added to PRISM first

**Problem**: "Invalid interaction type"
- **Solution**: Must use exact names from predefined list (see Section 3)
- **Solution**: Check for typos or extra spaces

**Problem**: "Duplicate interaction detected"
- **Solution**: Interaction already exists; use curation interface to update
- **Solution**: Check if you meant a different interaction type or stage

**Problem**: "CSV encoding error"
- **Solution**: Save CSV as UTF-8 encoding
- **Solution**: Remove special characters or ensure proper escaping

### Web Form Issues

**Problem**: Tool dropdown not loading or searchable
- **Solution**: Enable JavaScript in your browser
- **Solution**: Try a different browser (Chrome, Firefox recommended)
- **Solution**: Clear browser cache and reload

**Problem**: Form submission fails
- **Solution**: Check all required fields are completed (marked with *)
- **Solution**: Ensure source and target tools are different
- **Solution**: Check browser console for JavaScript errors

**Problem**: Can't find a tool in the dropdown
- **Solution**: Use Ctrl+F or Cmd+F in the dropdown to search
- **Solution**: Check alternative tool names or spellings
- **Solution**: Contact administrators to add missing tool

### Curation Issues

**Problem**: Can't edit an interaction
- **Solution**: Verify you have edit permissions
- **Solution**: Check if the interaction ID is correct
- **Solution**: Contact administrators for access

**Problem**: Changes not saving
- **Solution**: Ensure all required fields remain populated
- **Solution**: Check for validation errors on the page
- **Solution**: Try a different browser or clear cache

**Problem**: Accidentally changed something
- **Solution**: Re-edit and revert your changes
- **Solution**: Contact administrators to restore from backup if needed

### Getting Help

If you encounter issues not covered here:

1. **Check the Glossary**: `/glossary` for terminology questions
2. **View Examples**: Browse `/interactions` for reference
3. **API Documentation**: `/information-structures` for technical specs
4. **GitHub Issues**: [Report bugs or request features](https://github.com/adammoore/maldreth-infrastructure-interactions/issues)
5. **Contact**: Reach out to the MaLDReTH II working group

---

## Quick Reference Card

### Adding an Interaction

1. Go to `/interaction/add`
2. Select **Source Tool** (initiator)
3. Select **Target Tool** (receiver)
4. Choose **Interaction Type** (how they connect)
5. Choose **Lifecycle Stage** (where it's used)
6. Write **Description** (what and why)
7. Add optional details (technical, benefits, challenges)
8. Submit

### Curating an Interaction

1. Find interaction at `/interactions`
2. Click **Edit** (✏️)
3. Update fields as needed
4. Save changes

### CSV Import

1. Download template from `/upload/interactions/csv`
2. Fill in your data
3. Validate tool names and types
4. Upload and review results

### Key URLs

- **Add Interaction**: `/interaction/add`
- **View All**: `/interactions`
- **CSV Import**: `/upload/interactions/csv`
- **Tools Catalog**: `/tools`
- **Glossary**: `/glossary`
- **API**: `/api/v1/interactions`

---

## Appendix: Field Reference

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| Source Tool | Tool that initiates interaction | GitHub |
| Target Tool | Tool that receives | Zenodo |
| Interaction Type | How they connect | Data Exchange |
| Lifecycle Stage | Where it's used | PRESERVE |
| Description | What and why | "Automatic archiving of repositories" |

### Optional Enhancement Fields

| Field | Description | Example |
|-------|-------------|---------|
| Technical Details | Implementation info | "REST API with OAuth 2.0" |
| Benefits | Advantages | "Automated preservation, DOI minting" |
| Challenges | Limitations | "Large repository size limits" |
| Examples | Use cases | "Software packages archived with each release" |
| Contact Person | SME | "Jane Doe" |
| Organization | Institution | "Example University" |
| Email | Contact | "jane@example.edu" |
| Priority | Importance | High / Medium / Low |
| Complexity | Difficulty | Simple / Moderate / Complex |
| Status | Current state | Proposed / Pilot / Implemented / Deprecated |
| Submitted By | Contributor | "Your Name" |

### Interaction Types

1. API Integration
2. Data Exchange
3. Metadata Exchange
4. File Format Conversion
5. Workflow Integration
6. Plugin/Extension
7. Direct Database Connection
8. Web Service
9. Command Line Interface
10. Import/Export
11. Other

### Lifecycle Stages (MaLDReTH II)

1. PLAN - Research planning
2. COLLECT - Data collection
3. PROCESS - Data processing
4. ANALYSE - Data analysis
5. PRESERVE - Long-term preservation
6. SHARE - Data sharing
7. PUBLISH - Publication
8. DISCOVER - Data discovery
9. REUSE - Data reuse
10. INTEGRATE - Cross-dataset integration
11. MANAGE - Data management
12. ASSESS - Quality assessment

---

**PRISM** is an official output of the MaLDReTH II RDA Working Group, supporting systematic mapping of research infrastructure interactions across the global research data lifecycle.

🚀 **Get Started**: [Visit PRISM](https://mal2-data-survey-cb27f6674f20.herokuapp.com/) | [Add Interaction](https://mal2-data-survey-cb27f6674f20.herokuapp.com/interaction/add) | [View Documentation](https://mal2-data-survey-cb27f6674f20.herokuapp.com/information-structures)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-30
**Maintained By**: MaLDReTH II Working Group
**License**: Open Documentation (CC BY 4.0)
