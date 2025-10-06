# PRISM Tool Discovery & Enrichment System

**Architecture for Automated Research Tool Discovery and Metadata Enrichment**

---

## Overview

An automated system to discover, track, and enrich research tools and their interactions across the digital research ecosystem. Uses a combination of web crawling, API monitoring, and AI-powered analysis to keep PRISM's catalog up-to-date.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Discovery Coordinat or                        │
│              (Orchestrates all discovery activities)             │
└───────────┬─────────────────────────────────────────┬───────────┘
            │                                         │
            ├─────────────┬───────────────┬───────────┴──────┐
            │             │               │                  │
    ┌───────▼──────┐ ┌───▼────────┐ ┌───▼──────────┐ ┌────▼──────┐
    │   Watchers   │ │  Scrapers  │ │ API Monitors │ │ AI Agent  │
    │  (RSS/Atom)  │ │  (Web)     │ │ (External)   │ │ (Claude)  │
    └───────┬──────┘ └───┬────────┘ └───┬──────────┘ └────┬──────┘
            │            │              │                  │
            └────────────┴──────┬───────┴──────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   Discovery Queue      │
                    │  (Pending Discoveries) │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  Enrichment Pipeline   │
                    │  (Validate & Enhance)  │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   Human Review Queue   │
                    │ (Approve/Reject/Edit)  │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │    PRISM Database      │
                    └────────────────────────┘
```

---

## Core Components

### 1. Discovery Coordinator
**Purpose**: Orchestrates all discovery activities and manages scheduling

**Responsibilities**:
- Schedule periodic discovery runs
- Distribute work to watchers, scrapers, and monitors
- Aggregate results from all sources
- Deduplicate discovered items
- Prioritize discoveries based on confidence and relevance

**Technology**: Python with Celery for task scheduling

```python
class DiscoveryCoordinator:
    def __init__(self):
        self.watchers = [RSSWatcher(), GitHubWatcher(), ScholarWatcher()]
        self.scrapers = [WebScraper(), DocumentationScraper()]
        self.api_monitors = [GitHubAPIMonitor(), ZenodoAPIMonitor()]
        self.ai_agent = ClaudeAnalysisAgent()

    def run_discovery_cycle(self):
        """Execute a complete discovery cycle."""
        # 1. Collect from all sources
        discoveries = []
        for watcher in self.watchers:
            discoveries.extend(watcher.check_for_updates())

        # 2. Deduplicate and score
        unique_discoveries = self.deduplicate(discoveries)

        # 3. Enqueue for enrichment
        for discovery in unique_discoveries:
            DiscoveryQueue.add(discovery)

        # 4. Process enrichment pipeline
        self.enrichment_pipeline.process_queue()
```

---

### 2. Watchers (Passive Monitoring)

#### 2.1 RSS/Atom Feed Watcher
Monitors RSS/Atom feeds from research tool registries and blogs.

**Sources**:
- bio.tools RSS feed
- Software Sustainability Institute blog
- EOSC Marketplace updates
- RDA group announcements
- GitHub releases for known tools

**Implementation**:
```python
import feedparser
from datetime import datetime, timedelta

class RSSWatcher:
    FEEDS = {
        'biotools': 'https://bio.tools/api/tool?format=rss',
        'rda': 'https://www.rd-alliance.org/rss.xml',
        'software_carpentry': 'https://software-carpentry.org/feed.xml',
    }

    def check_for_updates(self, since=None):
        """Check all RSS feeds for new tools/updates."""
        if since is None:
            since = datetime.now() - timedelta(days=1)

        discoveries = []
        for source, url in self.FEEDS.items():
            feed = feedparser.parse(url)
            for entry in feed.entries:
                pub_date = datetime(*entry.published_parsed[:6])
                if pub_date > since:
                    discoveries.append({
                        'source': source,
                        'type': 'tool',
                        'name': entry.title,
                        'url': entry.link,
                        'description': entry.summary,
                        'discovered_at': pub_date,
                        'confidence': 0.8
                    })
        return discoveries
```

#### 2.2 GitHub Watcher
Monitors GitHub for research software releases and topics.

**Strategies**:
- Track specific topics: `research-software`, `data-science`, `bioinformatics`
- Monitor releases of known tools
- Discover tools mentioned in MaLDReTH-related repos

```python
class GitHubWatcher:
    TOPICS = ['research-software', 'data-management', 'fair-data']

    def check_for_updates(self):
        """Search GitHub for research tools."""
        discoveries = []

        # Search by topic
        for topic in self.TOPICS:
            repos = github_api.search_repositories(
                query=f"topic:{topic}",
                sort='updated',
                per_page=100
            )

            for repo in repos:
                if self._is_research_tool(repo):
                    discoveries.append(self._extract_tool_info(repo))

        return discoveries

    def _is_research_tool(self, repo):
        """Heuristic to determine if repo is a research tool."""
        indicators = [
            'research' in repo.description.lower(),
            'data' in repo.description.lower(),
            repo.stargazers_count > 50,
            any(topic in repo.topics for topic in ['science', 'research', 'data'])
        ]
        return sum(indicators) >= 2
```

#### 2.3 Academic Literature Watcher
Monitors academic papers for tool mentions.

**Sources**:
- arXiv RSS (cs.DL, cs.SE categories)
- PubMed Central (bioinformatics tools)
- PLOS ONE software articles

```python
class ScholarWatcher:
    def check_for_updates(self):
        """Monitor academic literature for tool mentions."""
        # Use arXiv API
        papers = arxiv_api.search(
            query='software AND research data',
            max_results=100,
            sort_by='lastUpdatedDate'
        )

        # Extract tool mentions using NLP
        discoveries = []
        for paper in papers:
            tools = self.extract_tool_mentions(paper.summary)
            for tool in tools:
                discoveries.append({
                    'source': 'arxiv',
                    'type': 'tool',
                    'name': tool,
                    'reference_paper': paper.entry_id,
                    'confidence': 0.6
                })

        return discoveries

    def extract_tool_mentions(self, text):
        """Use NER to extract tool names from text."""
        # This would use spaCy or similar for NER
        pass
```

---

### 3. Scrapers (Active Discovery)

#### 3.1 Web Scraper
Actively crawls known research tool directories and registries.

**Targets**:
- FAIRsharing.org registry
- EOSC Marketplace
- re3data.org
- Software Heritage
- Awesome lists (awesome-research-tools, awesome-bioinformatics)

```python
import scrapy
from scrapy.crawler import CrawlerProcess

class ToolRegistryScraper(scrapy.Spider):
    name = 'tool_registry'
    start_urls = [
        'https://fairsharing.org/search?page=1',
        'https://bio.tools/?page=1',
    ]

    def parse(self, response):
        # Extract tool cards/entries
        for tool_card in response.css('.tool-entry'):
            yield {
                'name': tool_card.css('.tool-name::text').get(),
                'description': tool_card.css('.tool-description::text').get(),
                'url': tool_card.css('a::attr(href)').get(),
                'category': tool_card.css('.category::text').get(),
                'source': 'fairsharing',
                'confidence': 0.9
            }

        # Follow pagination
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

#### 3.2 Documentation Scraper
Crawls tool documentation to discover interactions and integrations.

**Strategy**:
- Parse "Integrations" or "Extensions" pages
- Look for API documentation mentioning other tools
- Scan README files for tool interactions

```python
class DocumentationScraper:
    def scrape_integrations(self, tool_url):
        """Discover integrations from tool documentation."""
        # Find documentation pages
        doc_urls = self.find_documentation_urls(tool_url)

        interactions = []
        for url in doc_urls:
            content = self.fetch_page(url)

            # Look for integration keywords
            if self.has_integration_content(content):
                mentioned_tools = self.extract_tool_mentions(content)
                interaction_type = self.classify_interaction(content)

                for target_tool in mentioned_tools:
                    interactions.append({
                        'source_tool': self.current_tool,
                        'target_tool': target_tool,
                        'interaction_type': interaction_type,
                        'documentation_url': url,
                        'confidence': 0.7
                    })

        return interactions
```

---

### 4. API Monitors

#### 4.1 GitHub API Monitor
Tracks tool updates, releases, and interactions via GitHub API.

```python
class GitHubAPIMonitor:
    def monitor_tool_releases(self, tool_repos):
        """Monitor GitHub releases for known tools."""
        updates = []

        for repo_url in tool_repos:
            releases = github_api.get_releases(repo_url)
            latest = releases[0]

            # Check if this is new
            if self.is_new_release(repo_url, latest.tag_name):
                updates.append({
                    'tool': self.extract_tool_name(repo_url),
                    'update_type': 'release',
                    'version': latest.tag_name,
                    'notes': latest.body,
                    'url': latest.html_url,
                    'date': latest.published_at
                })

        return updates

    def discover_integrations(self, repo_url):
        """Analyze repo dependencies and integrations."""
        # Parse package.json, requirements.txt, etc.
        dependencies = self.get_dependencies(repo_url)

        # Check for known research tools in dependencies
        integrations = []
        for dep in dependencies:
            if self.is_research_tool(dep):
                integrations.append({
                    'source': repo_url,
                    'target': dep,
                    'interaction_type': 'Import/Export',
                    'confidence': 0.8
                })

        return integrations
```

#### 4.2 External Catalog API Monitors
Monitor APIs from external catalogs for changes.

```python
class CatalogAPIMonitor:
    CATALOGS = {
        'biotools': 'https://bio.tools/api/tool/',
        'zenodo': 'https://zenodo.org/api/records/',
        'eosc': 'https://marketplace.eosc-portal.eu/api/',
    }

    def check_for_new_tools(self, catalog_name):
        """Poll catalog API for new tools."""
        last_check = self.get_last_check_time(catalog_name)

        api_url = self.CATALOGS[catalog_name]
        tools = self.fetch_updated_since(api_url, last_check)

        discoveries = []
        for tool in tools:
            discoveries.append(self.normalize_tool_data(tool, catalog_name))

        self.update_last_check_time(catalog_name)
        return discoveries
```

---

### 5. AI Agent (Claude MCP Integration)

#### 5.1 Claude Analysis Agent
Uses Claude with MCP tools to analyze and enrich discoveries.

**Capabilities**:
- Analyze tool descriptions to classify by lifecycle stage
- Infer interaction types from documentation
- Generate comprehensive descriptions
- Suggest similar/related tools
- Quality check discovered data

**MCP Tools Available**:
- `web_fetch`: Fetch and analyze tool websites
- `github_api`: Query GitHub for tool metadata
- `semantic_search`: Find similar tools in existing catalog
- `classification`: Classify tools by category and stage

```python
from anthropic import Anthropic

class ClaudeAnalysisAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

    def analyze_discovery(self, discovery):
        """Use Claude to enrich discovered tool data."""
        prompt = f"""
        Analyze this research tool discovery and provide enrichment:

        Tool Name: {discovery['name']}
        URL: {discovery['url']}
        Description: {discovery['description']}

        Please provide:
        1. Which MaLDReTH lifecycle stages this tool supports (CONCEPTUALISE, PLAN, COLLECT, etc.)
        2. A comprehensive 2-3 sentence description
        3. Primary category (Repository, Analysis Platform, ELN, etc.)
        4. Whether it's open source (if determinable)
        5. Confidence score (0-1) for this classification
        6. Any similar/related tools in the PRISM catalog

        Format as JSON.
        """

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=[
                {
                    "name": "web_fetch",
                    "description": "Fetch and analyze a web page",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"}
                        }
                    }
                }
            ],
            messages=[{"role": "user", "content": prompt}]
        )

        return self.parse_claude_response(response)

    def infer_interactions(self, tool_name, documentation_text):
        """Use Claude to infer tool interactions from documentation."""
        prompt = f"""
        Analyze this documentation for {tool_name} and identify any integrations or interactions with other research tools:

        {documentation_text[:4000]}

        For each interaction found, provide:
        - Target tool name
        - Interaction type (API Integration, Data Exchange, etc.)
        - Brief description
        - Confidence score

        Format as JSON array.
        """

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        return self.parse_interactions(response)
```

---

### 6. Discovery Queue

**Purpose**: Manages pending discoveries awaiting enrichment and review.

**Database Schema**:
```sql
CREATE TABLE discovery_queue (
    id SERIAL PRIMARY KEY,
    item_type VARCHAR(50) NOT NULL,  -- 'tool' or 'interaction'
    source VARCHAR(100) NOT NULL,     -- 'github_watcher', 'rss_feed', etc.
    status VARCHAR(50) DEFAULT 'pending',  -- pending, enriching, reviewing, approved, rejected

    -- Tool discovery fields
    tool_name VARCHAR(200),
    tool_url VARCHAR(500),
    tool_description TEXT,

    -- Interaction discovery fields
    source_tool VARCHAR(200),
    target_tool VARCHAR(200),
    interaction_type VARCHAR(100),

    -- Metadata
    raw_data JSONB,               -- Original discovery data
    enriched_data JSONB,          -- After enrichment pipeline
    confidence_score FLOAT,       -- 0-1 confidence
    priority INTEGER DEFAULT 5,   -- 1-10 priority

    discovered_at TIMESTAMP DEFAULT NOW(),
    enriched_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by VARCHAR(100),

    -- Notes and feedback
    notes TEXT,
    rejection_reason TEXT
);

CREATE INDEX idx_discovery_status ON discovery_queue(status);
CREATE INDEX idx_discovery_priority ON discovery_queue(priority DESC, discovered_at DESC);
```

**API Endpoints**:
```python
@app.route('/api/v1/discoveries', methods=['GET'])
def get_discoveries():
    """Get pending discoveries for review."""
    status = request.args.get('status', 'reviewing')
    discoveries = DiscoveryQueue.query.filter_by(status=status).all()
    return jsonify([d.to_dict() for d in discoveries])

@app.route('/api/v1/discoveries/<int:id>/approve', methods=['POST'])
def approve_discovery(id):
    """Approve a discovery and add to main catalog."""
    discovery = DiscoveryQueue.query.get_or_404(id)

    if discovery.item_type == 'tool':
        tool = ExemplarTool(**discovery.enriched_data)
        db.session.add(tool)
    elif discovery.item_type == 'interaction':
        interaction = ToolInteraction(**discovery.enriched_data)
        db.session.add(interaction)

    discovery.status = 'approved'
    discovery.reviewed_at = datetime.now()
    db.session.commit()

    return jsonify({'status': 'approved'})

@app.route('/api/v1/discoveries/<int:id>/reject', methods=['POST'])
def reject_discovery(id):
    """Reject a discovery."""
    discovery = DiscoveryQueue.query.get_or_404(id)
    discovery.status = 'rejected'
    discovery.rejection_reason = request.json.get('reason')
    discovery.reviewed_at = datetime.now()
    db.session.commit()

    return jsonify({'status': 'rejected'})
```

---

### 7. Enrichment Pipeline

**Purpose**: Validate, normalize, and enhance discovered data before human review.

**Stages**:
1. **Validation**: Check data completeness and format
2. **Deduplication**: Check against existing catalog
3. **Normalization**: Standardize field formats
4. **AI Enrichment**: Use Claude to add metadata
5. **Confidence Scoring**: Calculate overall quality score
6. **Prioritization**: Assign review priority

```python
class EnrichmentPipeline:
    def process_discovery(self, discovery):
        """Process a discovery through the enrichment pipeline."""

        # Stage 1: Validation
        if not self.validate(discovery):
            discovery.status = 'invalid'
            return

        # Stage 2: Deduplication
        duplicate = self.check_duplicate(discovery)
        if duplicate:
            discovery.status = 'duplicate'
            discovery.notes = f"Duplicate of existing item: {duplicate.id}"
            return

        # Stage 3: Normalization
        normalized = self.normalize(discovery)

        # Stage 4: AI Enrichment
        enriched = self.ai_agent.analyze_discovery(normalized)
        discovery.enriched_data = enriched

        # Stage 5: Confidence Scoring
        confidence = self.calculate_confidence(discovery, enriched)
        discovery.confidence_score = confidence

        # Stage 6: Prioritization
        priority = self.calculate_priority(discovery)
        discovery.priority = priority

        # Set status based on confidence
        if confidence > 0.9:
            discovery.status = 'auto_approved'
            self.auto_approve(discovery)
        elif confidence > 0.6:
            discovery.status = 'reviewing'
        else:
            discovery.status = 'needs_review'

        discovery.enriched_at = datetime.now()
        db.session.commit()

    def calculate_confidence(self, discovery, enriched_data):
        """Calculate confidence score based on multiple factors."""
        factors = {
            'source_reliability': self.get_source_reliability(discovery.source),
            'data_completeness': self.check_completeness(enriched_data),
            'url_validity': self.check_url_validity(discovery.tool_url),
            'ai_confidence': enriched_data.get('confidence', 0.5)
        }

        # Weighted average
        weights = {'source_reliability': 0.3, 'data_completeness': 0.3,
                   'url_validity': 0.2, 'ai_confidence': 0.2}

        confidence = sum(factors[k] * weights[k] for k in factors)
        return confidence

    def calculate_priority(self, discovery):
        """Prioritize discoveries for review."""
        # Higher priority for:
        # - High confidence scores
        # - Reputable sources
        # - Tools mentioned in multiple sources
        # - Recently updated tools

        priority = 5  # Base priority

        if discovery.confidence_score > 0.8:
            priority += 3
        if discovery.source in ['github_api', 'biotools']:
            priority += 2
        if self.count_mentions(discovery.tool_name) > 1:
            priority += 2

        return min(priority, 10)
```

---

### 8. Human Review Interface

#### 8.1 Review Dashboard
Web interface for reviewing and approving discoveries.

**Features**:
- Queue view with filters (status, priority, source)
- Side-by-side comparison with existing catalog
- Quick approve/reject/edit actions
- Batch operations
- Search and filter capabilities

**Template** (`discovery_review.html`):
```html
<div class="container">
    <h1>Discovery Review Queue</h1>

    <!-- Filters -->
    <div class="filters">
        <select id="status-filter">
            <option value="reviewing">Awaiting Review</option>
            <option value="needs_review">Needs Attention</option>
            <option value="all">All</option>
        </select>
        <select id="priority-filter">
            <option value="high">High Priority</option>
            <option value="all">All Priorities</option>
        </select>
    </div>

    <!-- Discovery Cards -->
    <div id="discoveries">
        {% for discovery in discoveries %}
        <div class="discovery-card" data-id="{{ discovery.id }}">
            <div class="header">
                <h3>{{ discovery.tool_name }}</h3>
                <span class="confidence-badge">{{ discovery.confidence_score|round(2) }}</span>
                <span class="priority-badge">Priority: {{ discovery.priority }}</span>
            </div>

            <div class="content">
                <p><strong>Source:</strong> {{ discovery.source }}</p>
                <p><strong>URL:</strong> <a href="{{ discovery.tool_url }}" target="_blank">{{ discovery.tool_url }}</a></p>
                <p><strong>Description:</strong> {{ discovery.enriched_data.description }}</p>
                <p><strong>Category:</strong> {{ discovery.enriched_data.category }}</p>
                <p><strong>Lifecycle Stages:</strong> {{ discovery.enriched_data.stages|join(', ') }}</p>
            </div>

            <div class="actions">
                <button class="btn-approve" onclick="approveDiscovery({{ discovery.id }})">
                    <i class="fas fa-check"></i> Approve
                </button>
                <button class="btn-edit" onclick="editDiscovery({{ discovery.id }})">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn-reject" onclick="rejectDiscovery({{ discovery.id }})">
                    <i class="fas fa-times"></i> Reject
                </button>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
```

#### 8.2 Review Statistics Dashboard
```python
@app.route('/discoveries/stats')
def discovery_stats():
    """Statistics dashboard for discovery system."""
    stats = {
        'total_discoveries': DiscoveryQueue.query.count(),
        'pending_review': DiscoveryQueue.query.filter_by(status='reviewing').count(),
        'approved_today': DiscoveryQueue.query.filter(
            DiscoveryQueue.status == 'approved',
            DiscoveryQueue.reviewed_at >= datetime.now().date()
        ).count(),
        'by_source': db.session.query(
            DiscoveryQueue.source,
            func.count(DiscoveryQueue.id)
        ).group_by(DiscoveryQueue.source).all(),
        'avg_confidence': db.session.query(
            func.avg(DiscoveryQueue.confidence_score)
        ).scalar()
    }

    return render_template('discovery_stats.html', stats=stats)
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Weeks 1-2)
- [ ] Set up discovery queue database tables
- [ ] Implement DiscoveryCoordinator skeleton
- [ ] Create basic API endpoints for queue management
- [ ] Build simple review interface

### Phase 2: Watchers (Weeks 3-4)
- [ ] Implement RSS/Atom feed watcher
- [ ] Build GitHub watcher
- [ ] Add academic literature watcher
- [ ] Create scheduling system with Celery

### Phase 3: Scrapers (Weeks 5-6)
- [ ] Develop web scraper for tool registries
- [ ] Build documentation scraper
- [ ] Implement rate limiting and politeness delays
- [ ] Add error handling and retry logic

### Phase 4: API Monitors (Week 7)
- [ ] GitHub API monitor
- [ ] External catalog API monitors
- [ ] Webhook receivers for push notifications

### Phase 5: AI Integration (Weeks 8-9)
- [ ] Integrate Claude API
- [ ] Develop analysis prompts
- [ ] Build MCP tool connections
- [ ] Implement interaction inference

### Phase 6: Enrichment Pipeline (Week 10)
- [ ] Validation stage
- [ ] Deduplication logic
- [ ] Confidence scoring algorithm
- [ ] Auto-approval workflow

### Phase 7: Review Interface (Weeks 11-12)
- [ ] Build review dashboard
- [ ] Add batch operations
- [ ] Create statistics dashboard
- [ ] User feedback mechanisms

### Phase 8: Testing & Deployment (Weeks 13-14)
- [ ] Integration testing
- [ ] Load testing
- [ ] Documentation
- [ ] Production deployment

---

## Technology Stack

### Backend
- **Python 3.11+**: Core application
- **Flask**: Web framework
- **Celery**: Task scheduling and async processing
- **Redis**: Message broker for Celery
- **PostgreSQL**: Main database
- **SQLAlchemy**: ORM

### Discovery Tools
- **Scrapy**: Web scraping framework
- **feedparser**: RSS/Atom feed parsing
- **requests**: HTTP client
- **BeautifulSoup4**: HTML parsing
- **anthropic**: Claude API client

### AI/ML
- **Claude API**: AI-powered analysis
- **spaCy**: NER for tool mention extraction
- **sentence-transformers**: Semantic similarity

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **GitHub Actions**: CI/CD

---

## Configuration

### Environment Variables
```bash
# Discovery System Configuration
DISCOVERY_ENABLED=true
DISCOVERY_INTERVAL=3600  # Run every hour
AUTO_APPROVE_THRESHOLD=0.9

# API Keys
ANTHROPIC_API_KEY=sk-...
GITHUB_TOKEN=ghp_...

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Rate Limiting
SCRAPER_DELAY=2  # Seconds between requests
MAX_CONCURRENT_SCRAPERS=5
```

### Celery Configuration
```python
# celery_config.py
from celery import Celery
from celery.schedules import crontab

celery = Celery('prism_discovery',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0')

celery.conf.beat_schedule = {
    'run-discovery-cycle': {
        'task': 'tasks.run_discovery_cycle',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'process-enrichment-queue': {
        'task': 'tasks.process_enrichment_queue',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'cleanup-old-discoveries': {
        'task': 'tasks.cleanup_old_discoveries',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

---

## MCP Integration Strategy

### Using Model Context Protocol (MCP)

**Benefits**:
- Standardized tool interface for Claude
- Easy to add new discovery sources
- Consistent data exchange format
- Better observability and debugging

**MCP Server Setup**:
```python
# mcp_server.py
from mcp import MCPServer, Tool

server = MCPServer("prism-discovery")

@server.tool()
async def search_tool_registry(query: str, registry: str) -> dict:
    """Search a tool registry for matching tools."""
    if registry == "biotools":
        return await biotools_search(query)
    elif registry == "fairsharing":
        return await fairsharing_search(query)
    else:
        raise ValueError(f"Unknown registry: {registry}")

@server.tool()
async def fetch_tool_metadata(url: str) -> dict:
    """Fetch comprehensive metadata for a tool URL."""
    # Scrape website, check GitHub, query APIs
    metadata = await comprehensive_metadata_fetch(url)
    return metadata

@server.tool()
async def check_tool_exists(tool_name: str) -> dict:
    """Check if tool already exists in PRISM catalog."""
    existing = ExemplarTool.query.filter_by(name=tool_name).first()
    return {
        'exists': existing is not None,
        'tool_id': existing.id if existing else None,
        'tool_data': existing.to_dict() if existing else None
    }

@server.tool()
async def infer_interaction_type(description: str) -> str:
    """Infer interaction type from description."""
    # Use keyword matching or ML model
    return classify_interaction(description)

if __name__ == "__main__":
    server.run()
```

**Claude Integration**:
```python
class ClaudeDiscoveryAgent:
    def __init__(self):
        self.client = Anthropic()
        self.mcp_server_url = "http://localhost:8000/mcp"

    async def analyze_with_mcp(self, discovery):
        """Use Claude with MCP tools to analyze discovery."""

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            tools=[
                # MCP tools are automatically discovered
                {"type": "mcp", "server": self.mcp_server_url}
            ],
            messages=[{
                "role": "user",
                "content": f"""
                Analyze this research tool discovery:

                Name: {discovery['name']}
                URL: {discovery['url']}
                Source: {discovery['source']}

                Steps:
                1. Use fetch_tool_metadata to get comprehensive data
                2. Use check_tool_exists to see if it's already in PRISM
                3. If new, classify by lifecycle stages and category
                4. Provide enriched metadata in JSON format
                """
            }]
        )

        return self.parse_mcp_response(response)
```

---

## Monitoring & Alerting

### Metrics to Track
- Discoveries per day by source
- Enrichment pipeline throughput
- Average confidence scores
- Review queue size
- Approval/rejection rates
- API error rates

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

discoveries_total = Counter('prism_discoveries_total',
                           'Total discoveries',
                           ['source', 'item_type'])

enrichment_duration = Histogram('prism_enrichment_duration_seconds',
                               'Enrichment processing time')

review_queue_size = Gauge('prism_review_queue_size',
                         'Number of items awaiting review')

claude_api_calls = Counter('prism_claude_api_calls_total',
                          'Claude API calls',
                          ['success'])
```

### Alerting Rules
```yaml
# alerts.yml
groups:
  - name: discovery_system
    rules:
      - alert: HighReviewQueueSize
        expr: prism_review_queue_size > 100
        for: 1h
        annotations:
          summary: "Review queue is building up"

      - alert: LowDiscoveryRate
        expr: rate(prism_discoveries_total[1d]) < 1
        for: 6h
        annotations:
          summary: "Discovery system may be stalled"

      - alert: HighClaudeAPIErrorRate
        expr: rate(prism_claude_api_calls_total{success="false"}[5m]) > 0.1
        annotations:
          summary: "High rate of Claude API failures"
```

---

## Security Considerations

1. **API Key Management**: Use environment variables, never commit keys
2. **Rate Limiting**: Respect external API limits, implement backoff
3. **Data Validation**: Sanitize all scraped content before storage
4. **Access Control**: Review queue requires authentication
5. **Audit Logging**: Track all approvals/rejections with user info
6. **Privacy**: Don't store personal information from scraped content

---

## Future Enhancements

- **Community Contributions**: Allow users to submit discoveries via form
- **Voting System**: Community voting on pending discoveries
- **Integration Suggestions**: AI-powered suggestion of potential interactions
- **Trend Analysis**: Identify emerging tools and technologies
- **Automated Testing**: Generate test interactions for new tools
- **Knowledge Graph**: Build semantic relationships between tools

---

## Success Metrics

- **Coverage**: % of known research tools in PRISM catalog
- **Freshness**: Average age of tool information
- **Quality**: Accuracy of auto-classifications (vs human corrections)
- **Efficiency**: Time from discovery to catalog inclusion
- **Discovery Rate**: New tools found per week
- **False Positive Rate**: % of discoveries rejected by humans

---

**Version**: 1.0
**Last Updated**: October 2025
**Authors**: MaLDReTH II Working Group
**Status**: Design Document - Ready for Implementation
