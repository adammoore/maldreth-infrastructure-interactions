# Screencast 2: PRISM Updates & Roadmap
## New Features and Future Development

**Duration:** 12-15 minutes
**Target Audience:** Technical users, contributors, RDA WG members, potential collaborators
**Goal:** Showcase Phase 1 enhancements and preview discovery system roadmap

---

## Pre-Recording Checklist

- [ ] Have feature branch checked out (`feature/csv-import-and-discovery-system`)
- [ ] Database populated with CSV-imported tools (showing "Uncategorized" badges)
- [ ] Prepare sample CSV files to demonstrate upload
- [ ] Have DISCOVERY_SYSTEM_ARCHITECTURE.md and IMPLEMENTATION_ROADMAP.md open
- [ ] Test all new features work
- [ ] Clear browser cache
- [ ] Set up split-screen for code + browser
- [ ] Cursor highlighting enabled
- [ ] Do Not Disturb mode on

---

## Script

### INTRO (45 seconds)

**[Screen: PRISM homepage showing updated tool counts]**

> "Welcome back! I'm [Your Name] from the MaLDReTH II Working Group. In this video, I'll walk you through the latest enhancements to PRISM and share our exciting roadmap for automated tool discovery.
>
> Since our last update, we've implemented three major improvements:
> 1. Enriched metadata for better tool documentation
> 2. Bulk CSV import for rapid catalog growth
> 3. The foundation for an AI-powered discovery system
>
> Let's dive in."

**Action:** Scroll to show increased tool/interaction counts

---

### SECTION 1: Enriched Metadata (2 minutes)

**[Navigate to: Tools > View All Tools > Select an uncategorized tool]**

> "First, enriched metadata. We've expanded what information PRISM captures about each tool. Let me show you a tool that was recently imported via CSV."

**Action:** Click on a tool with "Uncategorized" badge

> "Notice several new fields:
>
> **License information** - We now track software licenses like MIT, Apache, GPL. This is critical for researchers and institutions making tool selection decisions, especially for reproducibility and compliance."

**Action:** Point to license field

> "**GitHub URLs** - Direct links to source code repositories. This helps developers evaluate tools, contribute improvements, and check activity status."

**Action:** Click GitHub link (opens in new tab, close it)

> "**Curator Notes** - A free-text field for contextual information that doesn't fit elsewhere. For example, 'Used by 50+ universities worldwide' or 'Integrates well with institutional authentication systems.'"

**Action:** Scroll to notes section

> "These fields are automatically populated during CSV import, then refined through community curation. This brings me to the next major feature..."

---

### SECTION 2: CSV Import System (3 minutes)

**[Navigate to: CSV Tools > Upload Tools CSV]**

> "The CSV import system allows us to rapidly scale the PRISM catalog. Previously, every tool had to be manually entered through the web form - slow and tedious for bulk data.
>
> Now, organizations can contribute their entire tool catalogs at once. Let me demonstrate."

**Action:** Show the upload form

> "The process is simple:
> 1. Prepare a CSV file with tool information
> 2. Upload it here
> 3. PRISM automatically processes it
>
> Let me show you what happens behind the scenes."

**Action:** Switch to showing the CSV file in Excel/text editor

> "Here's a sample catalog with 88 tools. Each row includes:
> - Tool name (required)
> - Description
> - Homepage URL
> - Open source status
> - **License** - NEW
> - **GitHub URL** - NEW
> - **Notes** - NEW
> - Category and Stage (optional for imports)
>
> Notice we have comprehensive metadata for each tool, gathered from registries like bio.tools, GitHub, and institutional catalogs."

**Action:** Scroll through CSV

**Action:** Switch back to PRISM, upload the CSV**

> "When I upload this file, PRISM:
> 1. Checks for duplicate tools by name
> 2. Creates new tools that don't exist
> 3. Enriches existing tools with new metadata
> 4. Flags everything as 'auto-created' for human review
> 5. Marks tools as 'Uncategorized' since stage and category are optional
>
> Let's see the results."

**Action:** Wait for upload to complete, show results page

> "Perfect! We've imported 73 new tools and enriched 16 existing ones. Notice the detailed breakdown - this transparency helps curators prioritize their work."

**Action:** Point to the statistics

---

### SECTION 3: Auto-Created vs Manual Curation (1.5 minutes)

**[Navigate to: Tools > View All Tools]**

> "This brings us to an important concept: the balance between automation and human expertise.
>
> Notice many tools now have an 'Uncategorized' badge. These are tools imported via CSV that haven't been assigned to a specific lifecycle stage or category yet."

**Action:** Filter or scroll to show uncategorized tools

> "This is intentional. While we can automatically gather basic information about tools, determining where they fit in the research lifecycle requires domain expertise. We don't want to guess wrong.
>
> So our workflow is:
> 1. Automated discovery/import gathers tools and metadata
> 2. Human curators review and categorize
> 3. Community validates and enriches
>
> This ensures scale AND quality."

**Action:** Click on an uncategorized tool, show its rich metadata

> "Even uncategorized, these tools have valuable information. A curator can review the description, license, and notes to make an informed categorization decision."

---

### SECTION 4: Interaction CSV Import (1.5 minutes)

**[Navigate to: CSV Tools > Upload Interactions CSV]**

> "The CSV import also works for interactions. This is powerful for documenting entire integration ecosystems.
>
> For example, if you're a repository developer, you might know about 20 different ways your tool integrates with others. Instead of entering each interaction manually, you can prepare a CSV and bulk upload."

**Action:** Show sample interactions CSV

> "The interactions CSV includes:
> - Source and target tools
> - Interaction type
> - Lifecycle stage
> - Description, technical details, benefits, challenges
> - Real-world examples
> - Contact information
>
> When uploaded, if a tool doesn't exist yet, PRISM automatically creates it. This is how we went from 6 interactions to 56 in one import."

**Action:** Show the interaction statistics

---

### SECTION 5: Database Changes & Migration (2 minutes)

**[Switch to: Terminal showing migration script OR show docs/IMPLEMENTATION_ROADMAP.md]**

> "Let me briefly show you the technical implementation, which might interest developers contributing to PRISM.
>
> We've added 7 new database fields across two tables. The migration was designed to be non-destructive - no data loss."

**Action:** Show or describe migrate_add_fields.py

> "The migration script:
> 1. Adds new columns with SQLite ALTER TABLE statements
> 2. Makes stage_id and category_id nullable (previously required)
> 3. Handles duplicate column errors gracefully
> 4. Updates existing auto-created tools with proper flags
> 5. Shows a comprehensive summary at the end
>
> This approach ensures production databases can be safely upgraded without downtime or data loss."

**Action:** Show the migration summary output

> "After migration, we had:
> - 167 total tools (started with 87)
> - 56 total interactions (started with 6)
> - All original data preserved
> - New fields ready for enriched metadata
>
> This foundation now supports the next big feature: automated discovery."

---

### SECTION 6: Discovery System Preview (4 minutes)

**[Screen: Open docs/DISCOVERY_SYSTEM_ARCHITECTURE.md]**

> "Now for the exciting part - the automated discovery system. This is coming in Phases 6-7 of our roadmap, but I want to give you a preview of how it will work."

**Action:** Show architecture diagram

> "The discovery system has 8 core components:
>
> **1. Discovery Coordinator** - Orchestrates the entire process
> **2. Watchers** - Monitor RSS feeds, GitHub, academic literature
> **3. Scrapers** - Extract data from tool registries
> **4. API Monitors** - Query GitHub API, bio.tools, etc.
> **5. AI Agent** - Claude with Model Context Protocol for enrichment
> **6. Discovery Queue** - Stores candidates awaiting review
> **7. Enrichment Pipeline** - Validates and enhances metadata
> **8. Human Review Interface** - Where curators approve or reject
>
> Let me show you how each piece works."

**Action:** Scroll through the architecture doc

> "**RSS Watchers** monitor feeds from the Research Data Alliance, Software Carpentry, and other trusted sources. When a new tool is mentioned, we extract the name, URL, and context."

**Action:** Show code snippet from discovery/watchers.py

> "Here's actual code from the RSS watcher. It:
> - Parses RSS feeds
> - Checks if entries mention research tools (keyword matching)
> - Extracts potential tool names
> - Assigns confidence scores based on the source's reliability
> - Creates a discovery queue item for human review
>
> The confidence score helps prioritize what curators look at first."

**Action:** Highlight the confidence scoring logic

> "**GitHub Watcher** is even smarter. It searches GitHub for repositories tagged with 'research-software', 'data-management', 'bioinformatics', etc."

**Action:** Show GitHub search query in code

> "For each repository, we calculate a confidence score based on:
> - Star count (more stars = higher confidence)
> - Has a license (shows maturity)
> - Has a homepage URL (indicates documentation)
> - Topics match our research domains
> - Not a fork (we want original tools)
>
> Tools scoring above a threshold go to the queue."

**Action:** Show confidence calculation function

> "But here's where it gets really powerful - the **AI Agent**."

**Action:** Show AI agent section in architecture doc

> "We're using Claude via the Model Context Protocol (MCP). This allows Claude to:
> 1. Fetch tool homepages
> 2. Read documentation
> 3. Analyze README files from GitHub
> 4. Extract structured metadata (description, license, features)
> 5. Suggest which lifecycle stage(s) the tool belongs to
> 6. Identify potential interactions based on API documentation
>
> The AI doesn't make final decisions - it enriches the discovery queue entry with suggestions and extracts metadata that would take humans hours to compile manually."

**Action:** Show example of AI-enriched discovery item in the docs

> "Then everything goes to the **Human Review Interface** - a queue where curators see:
> - The discovered tool name and URL
> - AI-extracted metadata
> - Suggested categorization (with confidence)
> - Similar tools already in PRISM
> - A simple approve/reject/modify workflow
>
> Approved items automatically create PRISM entries. Rejected items help train the system to be smarter."

---

### SECTION 7: Implementation Roadmap (2 minutes)

**[Screen: Open docs/IMPLEMENTATION_ROADMAP.md]**

> "So when does this all happen? Let me walk through the roadmap.
>
> **Phase 1 (Complete)** - What you just saw: CSV import, enriched metadata, database foundation. ✅
>
> **Phase 2 (Week 2)** - User authentication with ORCID, role-based access control. Viewers, Editors, and Admins with different permissions.
>
> **Phase 3 (Week 3)** - Admin curation tools. Bulk categorization, archive/delete capabilities, quality assurance workflows.
>
> **Phase 4-5 (Weeks 4-7)** - Discovery queue UI. Manual submission form for users to suggest tools, review and approval workflow, priority management.
>
> **Phase 6-7 (Weeks 6-10)** - Automated watchers and AI agent. RSS/GitHub monitoring, Claude integration via MCP, automated enrichment pipeline.
>
> **Phase 8-10 (Weeks 8-14)** - Data quality improvements, comprehensive testing, production deployment, community beta testing."

**Action:** Scroll through the roadmap phases

> "We've also estimated costs. The infrastructure for automated discovery runs about $1,350 per year for hosting, plus $200-500 monthly for Claude API calls when actively discovering.
>
> That's remarkably affordable for a system that could monitor hundreds of sources and discover thousands of tools."

**Action:** Show budget section

---

### SECTION 8: Technical Stack (1 minute)

**[Screen: Show the discovery/ code directory]**

> "For developers interested in contributing, here's our technical stack:
>
> - **Backend:** Python Flask + SQLAlchemy
> - **Database:** PostgreSQL (production) / SQLite (development)
> - **Watchers:** Python with feedparser, requests libraries
> - **AI:** Claude via Anthropic SDK with MCP
> - **Scheduling:** Celery + Redis (for automated jobs)
> - **Frontend:** Bootstrap 5 + vanilla JavaScript
>
> All code will be open source. The discovery system is designed to be modular - you can run just the RSS watcher, just the GitHub watcher, or the full AI pipeline depending on your needs."

**Action:** Show directory structure

---

### SECTION 9: Community Impact (1.5 minutes)

**[Screen: Back to PRISM showing stats]**

> "Let's talk about impact. With CSV import, we've more than doubled our catalog in days:
> - From 87 tools to 167 tools (+92%)
> - From 6 interactions to 56 interactions (+833%)
>
> But more importantly, we've created a sustainable growth model. Organizations can contribute their catalogs. The automated discovery system will continuously identify new tools. And the human review process ensures quality stays high.
>
> Imagine PRISM a year from now:
> - 1,000+ tools documented
> - 5,000+ interactions mapped
> - Weekly updates from automated discovery
> - Community of curators ensuring accuracy
> - Integration with other registries like bio.tools and FAIRsharing
>
> This becomes the comprehensive map of research infrastructure the community needs."

**Action:** Show visualization with more data

---

### SECTION 10: How to Contribute (1 minute)

**[Screen: Show contribution paths]**

> "How can you help make this vision real?
>
> **If you manage tools:**
> - Submit your tool catalog via CSV
> - Document integrations you know about
> - Keep your tool information updated
>
> **If you're a researcher:**
> - Review uncategorized tools in your domain
> - Add interactions you use in your work
> - Validate metadata accuracy
>
> **If you're a developer:**
> - Contribute to the open source codebase
> - Build watchers for new sources
> - Help improve the AI enrichment pipeline
> - Develop integrations with other platforms
>
> **If you're an institution:**
> - Host a community curation event
> - Sponsor infrastructure costs
> - Provide long-term hosting
> - Integrate PRISM into your tool discovery workflows
>
> Every contribution, big or small, helps build a better map of our research infrastructure."

---

### OUTRO (1 minute)

**[Screen: Roadmap timeline visual]**

> "So that's where PRISM is heading:
> - ✅ Phase 1 complete: CSV import and enriched metadata
> - 🔄 Phase 2 starting: Authentication and roles
> - 📅 Phase 6-7 coming: Automated AI-powered discovery
>
> We're building a platform that scales through automation while maintaining quality through community curation. A platform that makes research infrastructure discoverable, understandable, and interoperable."

**[Screen: Show PRISM logo/homepage]**

> "Join us on this journey. Try the new CSV import features. Review the roadmap. Share your feedback. And most importantly - contribute your knowledge about the tools and interactions you use every day.
>
> Links to everything I discussed are in the description. Thank you for watching, and I'll see you in the next update!"

**[Fade to end screen with:]**
- PRISM URL (feature branch demo site)
- GitHub repository (when open sourced)
- IMPLEMENTATION_ROADMAP.md link
- DISCOVERY_SYSTEM_ARCHITECTURE.md link
- RDA MaLDReTH II WG link
- Contact: maldreth-wg@rd-alliance.org

---

## Post-Production Notes

### Chapters (for YouTube)
- 00:00 - Introduction
- 00:45 - Enriched Metadata
- 02:45 - CSV Import System
- 05:45 - Auto-Created vs Manual Curation
- 07:15 - Interaction CSV Import
- 08:45 - Database Migration
- 10:45 - Discovery System Preview
- 14:45 - Implementation Roadmap
- 16:45 - Technical Stack
- 17:45 - Community Impact
- 19:15 - How to Contribute
- 20:15 - Outro

### Annotations
- Link to GitHub at first code mention
- Link to documentation files when shown
- "Try it now" call-to-action over demo site
- Highlight roadmap phases with timeline graphics

### B-Roll Suggestions
- Code editor showing migration script
- Terminal running migration
- CSV files in Excel with scrolling
- GitHub repository page
- Architecture diagrams animated
- Timeline visualization of roadmap phases
- Split screen: Before/after statistics

### Key Frames to Highlight
- Upload results page (tool counts)
- Uncategorized tools view
- Discovery system architecture diagram
- Confidence scoring code
- Roadmap phases timeline
- Final statistics comparison

---

## Screen Recording Setup

### Layout Options

**Option 1: Browser Only**
- Good for: Non-technical audience
- Focus: UI and features
- Record: Full screen at 1920x1080

**Option 2: Split Screen**
- Good for: Technical audience
- Left: Code/docs
- Right: Browser
- Record: Full screen, both visible

**Option 3: Picture-in-Picture**
- Good for: Mixed audience
- Main: Browser
- Corner: Code/terminal when relevant
- Swap as needed

Recommended: **Option 2** for this screencast (technical focus)

---

## Demo Data Needed

Before recording:
- [ ] 50+ uncategorized tools in database
- [ ] At least one CSV file ready to upload
- [ ] Sample interactions CSV
- [ ] Migration script output saved
- [ ] Discovery system code visible in editor
- [ ] Documentation files opened in tabs
- [ ] Before/after statistics prepared

---

## Common Mistakes to Avoid

❌ **Don't:**
- Assume viewers understand database migrations
- Rush through code - explain what it does
- Skip over "why" this matters
- Use internal jargon (e.g., "Phase 1", "MCP") without explanation
- Show buggy features or incomplete code

✅ **Do:**
- Explain technical concepts in plain language
- Show real examples with actual data
- Connect features to user benefits
- Demonstrate both UI and underlying tech
- Mention future opportunities for contribution

---

## Accessibility Considerations

- Increase font size in code editor (18-20pt)
- Use high contrast themes
- Read all code comments aloud
- Describe architecture diagrams verbally
- Provide captions for technical terms
- Include transcript with code snippets

---

## Questions to Address

Anticipate viewer questions:
1. "How do I upload a CSV?" → Show step-by-step
2. "What format is the CSV?" → Display example
3. "How accurate is the AI?" → Discuss confidence scores
4. "Can I run this myself?" → Mention open source plans
5. "How can I help?" → Clear contribution paths
6. "When will discovery be live?" → Show roadmap timeline
7. "What if the AI is wrong?" → Explain human review

---

## Testing Checklist

Before final recording:
- [ ] All links work
- [ ] CSV upload functions correctly
- [ ] Uncategorized tools display properly
- [ ] Code examples are accurate
- [ ] Documentation is up to date
- [ ] Statistics match current database
- [ ] No sensitive/test data visible
- [ ] Audio levels consistent throughout

---

## Export Settings

- Resolution: 1920x1080 (1080p)
- Frame rate: 30 fps
- Codec: H.264
- Bitrate: 5-8 Mbps (high quality)
- Audio: AAC, 192 kbps, 48kHz
- Format: MP4

---

## Publishing Metadata

**Title:** "PRISM Updates: CSV Import, Enriched Metadata & AI-Powered Discovery Roadmap"

**Description:**
```
In this technical update, we walk through the latest enhancements to PRISM (Platform for Research Infrastructure Synergy Mapping) and preview the upcoming AI-powered automated discovery system.

🆕 What's New (Phase 1 - Complete):
• Enriched metadata: licenses, GitHub URLs, curator notes
• Bulk CSV import for tools and interactions
• Auto-created flags and curation workflows
• Database migration with zero data loss
• 92% growth in tool catalog (+80 tools in one import!)

🔮 What's Coming (Phases 2-7):
• User authentication with ORCID
• Role-based access control
• Admin curation dashboard
• Automated discovery via RSS, GitHub, academic literature
• AI-powered enrichment using Claude and MCP
• Human-in-the-loop review process

📊 Impact:
• 167 tools (up from 87)
• 56 interactions (up from 6)
• Sustainable growth through automation + community curation

🔗 Resources:
• PRISM: [URL]
• Implementation Roadmap: [GitHub link]
• Discovery System Architecture: [GitHub link]
• MaLDReTH II RDA WG: [RDA link]

📧 Contact: maldreth-wg@rd-alliance.org

#ResearchData #OpenScience #RDA #FAIR #ResearchInfrastructure #MaLDReTH
```

**Tags:**
research data, open science, RDA, research infrastructure, tool discovery, FAIR data, data lifecycle, metadata, CSV import, AI discovery, academic tools, research tools, interoperability
