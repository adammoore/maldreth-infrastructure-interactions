#!/usr/bin/env python3
"""
Tool Enrichment Guide - Helper script for enriching PRISM tool metadata

This script provides utilities for enriching tool data from various sources.
It's designed to be run manually with human verification of results.
"""

import requests
import time
from typing import Dict, Optional

class ToolEnricher:
    """Enrich tool metadata from external sources."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PRISM-MaLDReTH-Tool-Enrichment/1.0'
        })

    def search_github(self, tool_name: str) -> Optional[Dict]:
        """
        Search GitHub for a repository matching the tool name.

        Returns repository metadata if found.
        """
        try:
            url = f"https://api.github.com/search/repositories"
            params = {
                'q': tool_name,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 1
            }

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if data['total_count'] > 0:
                    repo = data['items'][0]
                    return {
                        'name': repo['name'],
                        'description': repo['description'],
                        'url': repo['html_url'],
                        'homepage': repo['homepage'],
                        'license': repo['license']['name'] if repo['license'] else None,
                        'is_open_source': repo['license'] is not None,
                        'stars': repo['stargazers_count'],
                        'language': repo['language'],
                        'topics': repo.get('topics', []),
                        'last_updated': repo['updated_at']
                    }
            elif response.status_code == 403:
                print(f"GitHub API rate limit exceeded. Wait before continuing.")
            else:
                print(f"GitHub search failed: {response.status_code}")

        except Exception as e:
            print(f"Error searching GitHub for {tool_name}: {e}")

        return None

    def search_wikidata(self, tool_name: str) -> Optional[Dict]:
        """
        Search Wikidata for software matching the tool name.

        Returns Wikidata entity data if found.
        """
        try:
            url = "https://www.wikidata.org/w/api.php"
            params = {
                'action': 'wbsearchentities',
                'format': 'json',
                'language': 'en',
                'type': 'item',
                'search': tool_name
            }

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if 'search' in data and len(data['search']) > 0:
                    entity = data['search'][0]
                    return {
                        'qid': entity['id'],
                        'label': entity['label'],
                        'description': entity.get('description', ''),
                        'url': f"https://www.wikidata.org/wiki/{entity['id']}"
                    }

        except Exception as e:
            print(f"Error searching Wikidata for {tool_name}: {e}")

        return None

    def get_biotools_entry(self, tool_name: str) -> Optional[Dict]:
        """
        Search bio.tools registry for life sciences tools.

        Returns tool metadata if found.
        """
        try:
            url = "https://bio.tools/api/tool"
            params = {'q': tool_name}

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if 'list' in data and len(data['list']) > 0:
                    tool = data['list'][0]
                    return {
                        'biotoolsID': tool['biotoolsID'],
                        'name': tool['name'],
                        'description': tool.get('description', ''),
                        'homepage': tool.get('homepage', ''),
                        'topics': [t['term'] for t in tool.get('topic', [])],
                        'operations': [op['term'] for op in tool.get('function', [{}])[0].get('operation', [])],
                    }

        except Exception as e:
            print(f"Error searching bio.tools for {tool_name}: {e}")

        return None

    def enrich_tool(self, tool_name: str, sleep_time: float = 1.0) -> Dict:
        """
        Enrich a tool by searching multiple sources.

        Args:
            tool_name: Name of the tool to enrich
            sleep_time: Seconds to wait between API calls (rate limiting)

        Returns:
            Dictionary with enriched metadata from all sources
        """
        print(f"\nEnriching: {tool_name}")
        enriched = {
            'original_name': tool_name,
            'github': None,
            'wikidata': None,
            'biotools': None
        }

        # Search GitHub
        print("  Searching GitHub...")
        enriched['github'] = self.search_github(tool_name)
        time.sleep(sleep_time)

        # Search Wikidata
        print("  Searching Wikidata...")
        enriched['wikidata'] = self.search_wikidata(tool_name)
        time.sleep(sleep_time)

        # Search bio.tools
        print("  Searching bio.tools...")
        enriched['biotools'] = self.get_biotools_entry(tool_name)
        time.sleep(sleep_time)

        return enriched

    def merge_sources(self, enriched: Dict) -> Dict:
        """
        Merge data from multiple sources into a single record.

        Priority: bio.tools > GitHub > Wikidata
        """
        merged = {
            'name': enriched['original_name'],
            'description': None,
            'url': None,
            'is_open_source': None,
            'license': None,
            'topics': [],
            'sources': []
        }

        # Merge from Wikidata (lowest priority)
        if enriched['wikidata']:
            merged['description'] = enriched['wikidata'].get('description')
            merged['url'] = enriched['wikidata'].get('url')
            merged['sources'].append('wikidata')

        # Merge from GitHub (higher priority)
        if enriched['github']:
            merged['description'] = enriched['github'].get('description') or merged['description']
            merged['url'] = enriched['github'].get('homepage') or enriched['github'].get('url') or merged['url']
            merged['is_open_source'] = enriched['github'].get('is_open_source')
            merged['license'] = enriched['github'].get('license')
            merged['topics'].extend(enriched['github'].get('topics', []))
            merged['sources'].append('github')
            merged['github_stars'] = enriched['github'].get('stars')
            merged['language'] = enriched['github'].get('language')

        # Merge from bio.tools (highest priority for description)
        if enriched['biotools']:
            merged['description'] = enriched['biotools'].get('description') or merged['description']
            merged['url'] = enriched['biotools'].get('homepage') or merged['url']
            merged['topics'].extend(enriched['biotools'].get('topics', []))
            merged['sources'].append('biotools')

        return merged


# Known research tools with manual metadata (curated list)
CURATED_TOOLS = {
    # Data Management Planning
    "DMPTool": {
        "description": "Data Management Planning tool from California Digital Library",
        "url": "https://dmptool.org/",
        "is_open_source": True,
        "license": "MIT",
        "github": "https://github.com/CDLUC3/dmptool"
    },
    "DMP Online": {
        "description": "Data Management Planning tool from Digital Curation Centre",
        "url": "https://dmponline.dcc.ac.uk/",
        "is_open_source": True,
        "license": "MIT",
        "github": "https://github.com/DMPRoadmap/roadmap"
    },

    # Repositories
    "Zenodo": {
        "description": "General-purpose open repository for research outputs",
        "url": "https://zenodo.org/",
        "is_open_source": True,
        "license": "GNU GPL v2",
        "github": "https://github.com/zenodo/zenodo"
    },
    "Figshare": {
        "description": "Repository for research outputs including datasets, figures, and presentations",
        "url": "https://figshare.com/",
        "is_open_source": False,
    },
    "Dataverse": {
        "description": "Open source research data repository platform",
        "url": "https://dataverse.org/",
        "is_open_source": True,
        "license": "Apache 2.0",
        "github": "https://github.com/IQSS/dataverse"
    },
    "DSpace": {
        "description": "Open source repository platform for digital content",
        "url": "https://dspace.org/",
        "is_open_source": True,
        "license": "BSD",
        "github": "https://github.com/DSpace/DSpace"
    },

    # Version Control
    "GitHub": {
        "description": "Web-based platform for version control using Git",
        "url": "https://github.com/",
        "is_open_source": False,
    },
    "GitLab": {
        "description": "Web-based DevOps lifecycle tool with Git repository manager",
        "url": "https://gitlab.com/",
        "is_open_source": True,
        "license": "MIT",
        "github": "https://gitlab.com/gitlab-org/gitlab"
    },

    # Data Analysis
    "R": {
        "description": "Programming language and environment for statistical computing",
        "url": "https://www.r-project.org/",
        "is_open_source": True,
        "license": "GPL",
    },
    "Python": {
        "description": "High-level programming language for general-purpose programming",
        "url": "https://www.python.org/",
        "is_open_source": True,
        "license": "PSF",
    },
    "Jupyter": {
        "description": "Interactive computing environment for creating notebook documents",
        "url": "https://jupyter.org/",
        "is_open_source": True,
        "license": "BSD",
        "github": "https://github.com/jupyter/jupyter"
    },
    "RStudio": {
        "description": "Integrated development environment for R",
        "url": "https://posit.co/products/open-source/rstudio/",
        "is_open_source": True,
        "license": "AGPL v3",
        "github": "https://github.com/rstudio/rstudio"
    },

    # Persistent Identifiers
    "ORCID": {
        "description": "Persistent identifier for researchers and contributors",
        "url": "https://orcid.org/",
        "is_open_source": True,
        "license": "MIT",
        "github": "https://github.com/ORCID"
    },
    "DOI": {
        "description": "Digital Object Identifier system for persistent identification",
        "url": "https://www.doi.org/",
        "is_open_source": False,
    },

    # Electronic Lab Notebooks
    "RSpace": {
        "description": "Electronic lab notebook for research teams",
        "url": "https://www.researchspace.com/",
        "is_open_source": True,
        "license": "Apache 2.0",
        "github": "https://github.com/rspace-os/rspace-web"
    },
    "LabArchives": {
        "description": "Electronic lab notebook and collaboration platform",
        "url": "https://www.labarchives.com/",
        "is_open_source": False,
    },

    # Reference Management
    "Zotero": {
        "description": "Free, open-source reference management software",
        "url": "https://www.zotero.org/",
        "is_open_source": True,
        "license": "AGPL v3",
        "github": "https://github.com/zotero/zotero"
    },
    "Mendeley": {
        "description": "Reference manager and academic social network",
        "url": "https://www.mendeley.com/",
        "is_open_source": False,
    },
    "EndNote": {
        "description": "Commercial reference management software",
        "url": "https://endnote.com/",
        "is_open_source": False,
    },
}


def main():
    """Example usage of tool enrichment."""
    enricher = ToolEnricher()

    # Example: Enrich a single tool
    tool_name = "Jupyter"
    result = enricher.enrich_tool(tool_name)
    merged = enricher.merge_sources(result)

    print("\n" + "="*60)
    print(f"Merged result for {tool_name}:")
    print("="*60)
    for key, value in merged.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    print("Tool Enrichment Helper")
    print("="*60)
    print("This script helps enrich PRISM tool metadata from external sources.")
    print("It includes curated data for common research tools.")
    print("\nTo use:")
    print("1. Review CURATED_TOOLS dictionary for manually verified tools")
    print("2. Use ToolEnricher class to fetch data from APIs")
    print("3. Always verify automated results before importing")
    print("="*60)

    main()
