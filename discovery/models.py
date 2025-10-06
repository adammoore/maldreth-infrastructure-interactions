"""
Database models for the discovery system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DiscoveryQueueItem(Base):
    """Model for items in the discovery queue."""
    __tablename__ = 'discovery_queue'

    id = Column(Integer, primary_key=True)
    item_type = Column(String(50), nullable=False)  # 'tool' or 'interaction'
    source = Column(String(100), nullable=False)  # e.g., 'github_watcher', 'rss_feed'
    status = Column(String(50), default='pending')  # pending, enriching, reviewing, approved, rejected

    # Tool discovery fields
    tool_name = Column(String(200))
    tool_url = Column(String(500))
    tool_description = Column(Text)

    # Interaction discovery fields
    source_tool = Column(String(200))
    target_tool = Column(String(200))
    interaction_type = Column(String(100))

    # Metadata
    raw_data = Column(JSON)  # Original discovery data
    enriched_data = Column(JSON)  # After enrichment pipeline
    confidence_score = Column(Float, default=0.0)  # 0-1 confidence
    priority = Column(Integer, default=5)  # 1-10 priority

    discovered_at = Column(DateTime, default=datetime.utcnow)
    enriched_at = Column(DateTime)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String(100))

    # Notes and feedback
    notes = Column(Text)
    rejection_reason = Column(Text)

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'item_type': self.item_type,
            'source': self.source,
            'status': self.status,
            'tool_name': self.tool_name,
            'tool_url': self.tool_url,
            'tool_description': self.tool_description,
            'source_tool': self.source_tool,
            'target_tool': self.target_tool,
            'interaction_type': self.interaction_type,
            'raw_data': self.raw_data,
            'enriched_data': self.enriched_data,
            'confidence_score': self.confidence_score,
            'priority': self.priority,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
            'enriched_at': self.enriched_at.isoformat() if self.enriched_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': self.reviewed_by,
            'notes': self.notes,
            'rejection_reason': self.rejection_reason
        }


class DiscoverySource(Base):
    """Track discovery sources and their reliability."""
    __tablename__ = 'discovery_sources'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(50))  # 'watcher', 'scraper', 'api_monitor'
    reliability_score = Column(Float, default=0.5)  # 0-1, updated based on approval rate
    last_run = Column(DateTime)
    total_discoveries = Column(Integer, default=0)
    total_approved = Column(Integer, default=0)
    total_rejected = Column(Integer, default=0)
    is_enabled = Column(String(10), default='true')  # Boolean stored as string
    config = Column(JSON)  # Source-specific configuration

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type,
            'reliability_score': self.reliability_score,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'total_discoveries': self.total_discoveries,
            'total_approved': self.total_approved,
            'total_rejected': self.total_rejected,
            'is_enabled': self.is_enabled == 'true',
            'approval_rate': self.total_approved / self.total_discoveries if self.total_discoveries > 0 else 0,
            'config': self.config
        }
