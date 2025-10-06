"""
Watchers for passive monitoring of tool updates.
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseWatcher:
    """Base class for all watchers."""

    def __init__(self, name: str):
        self.name = name
        self.last_check = None

    def check_for_updates(self, since: Optional[datetime] = None) -> List[Dict]:
        """
        Check for updates since given datetime.

        Returns list of discoveries in standardized format.
        """
        raise NotImplementedError


class RSSWatcher(BaseWatcher):
    """Watcher for RSS/Atom feeds."""

    FEEDS = {
        'rda': {
            'url': 'https://www.rd-alliance.org/rss.xml',
            'reliability': 0.8
        },
        'software_carpentry': {
            'url': 'https://software-carpentry.org/feed.xml',
            'reliability': 0.7
        },
        # Note: bio.tools doesn't have RSS, but we'll add it when available
    }

    def __init__(self):
        super().__init__('rss_watcher')

    def check_for_updates(self, since: Optional[datetime] = None) -> List[Dict]:
        """Check all RSS feeds for new tools/updates."""
        if since is None:
            since = datetime.now() - timedelta(days=1)

        discoveries = []

        for source, config in self.FEEDS.items():
            try:
                feed = feedparser.parse(config['url'])

                for entry in feed.entries:
                    # Parse publication date
                    if hasattr(entry, 'published_parsed'):
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed'):
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()

                    if pub_date > since:
                        # Check if entry mentions research tools
                        if self._is_tool_related(entry):
                            discoveries.append({
                                'source': f'rss_{source}',
                                'type': 'tool',
                                'name': self._extract_tool_name(entry.title),
                                'url': entry.link,
                                'description': entry.get('summary', entry.title),
                                'discovered_at': pub_date,
                                'confidence': config['reliability'] * 0.6,  # Lower for RSS mentions
                                'raw_data': {
                                    'feed_source': source,
                                    'entry_title': entry.title,
                                    'entry_link': entry.link,
                                    'entry_summary': entry.get('summary', '')
                                }
                            })

            except Exception as e:
                logger.error(f"Error checking RSS feed {source}: {e}")
                continue

        logger.info(f"RSS Watcher found {len(discoveries)} discoveries")
        return discoveries

    def _is_tool_related(self, entry) -> bool:
        """Check if RSS entry is related to research tools."""
        keywords = [
            'software', 'tool', 'platform', 'repository', 'system',
            'application', 'service', 'infrastructure', 'framework'
        ]

        text = (entry.title + ' ' + entry.get('summary', '')).lower()
        return any(keyword in text for keyword in keywords)

    def _extract_tool_name(self, title: str) -> str:
        """Extract potential tool name from title."""
        # Simple heuristic: look for capitalized words or quoted terms
        import re

        # Check for quoted terms
        quoted = re.findall(r'"([^"]+)"', title)
        if quoted:
            return quoted[0]

        # Check for title-cased words
        words = title.split()
        candidates = [w for w in words if w[0].isupper() and len(w) > 3]
        if candidates:
            return candidates[0]

        return title[:50]  # Fallback to first 50 chars


class GitHubWatcher(BaseWatcher):
    """Watcher for GitHub repositories and releases."""

    TOPICS = ['research-software', 'data-management', 'fair-data', 'bioinformatics']
    SEARCH_QUERIES = [
        'research data tool',
        'data management platform',
        'scientific workflow'
    ]

    def __init__(self, github_token: Optional[str] = None):
        super().__init__('github_watcher')
        self.token = github_token
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })

    def check_for_updates(self, since: Optional[datetime] = None) -> List[Dict]:
        """Search GitHub for research tools."""
        if since is None:
            since = datetime.now() - timedelta(days=7)

        discoveries = []

        # Search by topic
        for topic in self.TOPICS:
            try:
                repos = self._search_repositories(f"topic:{topic}", since)
                discoveries.extend(repos)
            except Exception as e:
                logger.error(f"Error searching GitHub topic {topic}: {e}")

        # Search by query
        for query in self.SEARCH_QUERIES:
            try:
                repos = self._search_repositories(query, since)
                discoveries.extend(repos)
            except Exception as e:
                logger.error(f"Error searching GitHub query '{query}': {e}")

        # Deduplicate by URL
        unique_discoveries = {d['url']: d for d in discoveries}.values()

        logger.info(f"GitHub Watcher found {len(unique_discoveries)} unique discoveries")
        return list(unique_discoveries)

    def _search_repositories(self, query: str, since: datetime, max_results: int = 30) -> List[Dict]:
        """Search GitHub repositories."""
        discoveries = []

        try:
            # Format date for GitHub API
            since_str = since.strftime('%Y-%m-%d')

            url = 'https://api.github.com/search/repositories'
            params = {
                'q': f'{query} pushed:>{since_str}',
                'sort': 'updated',
                'order': 'desc',
                'per_page': max_results
            }

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                for repo in data.get('items', []):
                    if self._is_research_tool(repo):
                        discoveries.append(self._extract_tool_info(repo))
            elif response.status_code == 403:
                logger.warning("GitHub API rate limit exceeded")
            else:
                logger.error(f"GitHub API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Error in GitHub search: {e}")

        return discoveries

    def _is_research_tool(self, repo: Dict) -> bool:
        """Heuristic to determine if repo is a research tool."""
        description = (repo.get('description') or '').lower()

        indicators = [
            any(keyword in description for keyword in ['research', 'data', 'scientific', 'analysis']),
            repo.get('stargazers_count', 0) > 20,
            repo.get('topics') and any(t in self.TOPICS for t in repo.get('topics', [])),
            not repo.get('fork', False),  # Prefer original repos
            repo.get('language') in ['Python', 'R', 'Julia', 'Java', 'JavaScript']
        ]

        return sum(indicators) >= 2

    def _extract_tool_info(self, repo: Dict) -> Dict:
        """Extract standardized tool info from GitHub repo."""
        return {
            'source': 'github_watcher',
            'type': 'tool',
            'name': repo['name'],
            'url': repo['html_url'],
            'description': repo.get('description', ''),
            'discovered_at': datetime.now(),
            'confidence': self._calculate_confidence(repo),
            'raw_data': {
                'github_repo': repo['full_name'],
                'stars': repo.get('stargazers_count', 0),
                'language': repo.get('language'),
                'topics': repo.get('topics', []),
                'homepage': repo.get('homepage'),
                'license': repo.get('license', {}).get('name') if repo.get('license') else None,
                'is_open_source': repo.get('license') is not None
            }
        }

    def _calculate_confidence(self, repo: Dict) -> float:
        """Calculate confidence score for a GitHub repo."""
        score = 0.5  # Base score

        # More stars = higher confidence
        stars = repo.get('stargazers_count', 0)
        if stars > 100:
            score += 0.2
        elif stars > 50:
            score += 0.1

        # Has license = higher confidence
        if repo.get('license'):
            score += 0.1

        # Has homepage = higher confidence
        if repo.get('homepage'):
            score += 0.1

        # Research-related topics
        topics = repo.get('topics', [])
        if any(t in self.TOPICS for t in topics):
            score += 0.1

        return min(score, 1.0)


class ScholarWatcher(BaseWatcher):
    """Watcher for academic literature mentions of tools."""

    def __init__(self):
        super().__init__('scholar_watcher')
        # Placeholder - would integrate with arXiv, PubMed APIs

    def check_for_updates(self, since: Optional[datetime] = None) -> List[Dict]:
        """Monitor academic literature for tool mentions."""
        # This is a placeholder for future implementation
        logger.info("Scholar watcher not yet implemented")
        return []
