"""
PRISM Discovery System

Automated research tool discovery and enrichment system.
"""

from .coordinator import DiscoveryCoordinator
from .queue import DiscoveryQueue
from .watchers import RSSWatcher, GitHubWatcher
from .enrichment import EnrichmentPipeline

__all__ = [
    'DiscoveryCoordinator',
    'DiscoveryQueue',
    'RSSWatcher',
    'GitHubWatcher',
    'EnrichmentPipeline',
]

__version__ = '0.1.0'
