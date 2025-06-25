"""
Enhanced database models for Phase 2 MaLDReTH Integration.

This module extends the existing models to integrate with MaLDReTH 1 data,
including lifecycle stages, substages, tools, and their relationships.
"""

from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.ext.hybrid import hybrid_property

# Import db from app context, but check if models already has db defined
try:
    from models import db
except ImportError:
    from app import db

# Only define these models if they haven't been defined already
if (
    not hasattr(db.Model, "_decl_class_registry")
    or "LifecycleStage" not in db.Model._decl_class_registry
):

    class LifecycleStage(db.Model):
        """
        Enhanced lifecycle stage model integrating MaLDReTH definitions.
        """

        __tablename__ = "lifecycle_stages"

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False, unique=True, index=True)
        description = db.Column(db.Text, nullable=False)
        maldreth_description = db.Column(db.Text)
        order = db.Column(db.Integer, nullable=False, unique=True)
        color_code = db.Column(db.String(7), default="#007bff")
        icon = db.Column(db.String(50), default="bi-circle")
        is_active = db.Column(db.Boolean, default=True, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        updated_at = db.Column(
            db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

        # Relationships
        substages = db.relationship(
            "LifecycleSubstage",
            backref="stage",
            lazy="dynamic",
            cascade="all, delete-orphan",
        )
        tool_categories = db.relationship(
            "ToolCategory",
            backref="stage",
            lazy="dynamic",
            cascade="all, delete-orphan",
        )
        tools = db.relationship("Tool", backref="stage", lazy="dynamic")

        @hybrid_property
        def tool_count(self):
            """Get the total number of tools for this stage."""
            return self.tools.count() if hasattr(self.tools, "count") else 0

        @hybrid_property
        def substage_count(self):
            """Get the number of substages for this stage."""
            return self.substages.count() if hasattr(self.substages, "count") else 0

        def to_dict(self, include_counts=False):
            """Convert stage to dictionary representation."""
            data = {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "maldreth_description": self.maldreth_description,
                "order": self.order,
                "color_code": self.color_code,
                "icon": self.icon,
                "is_active": self.is_active,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            }

            if include_counts:
                data.update(
                    {
                        "tool_count": self.tool_count,
                        "substage_count": self.substage_count,
                    }
                )

            return data

    class LifecycleSubstage(db.Model):
        """
        Substages within each lifecycle stage.
        """

        __tablename__ = "lifecycle_substages"

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False, index=True)
        description = db.Column(db.Text)
        stage_id = db.Column(
            db.Integer, db.ForeignKey("lifecycle_stages.id"), nullable=False
        )
        order = db.Column(db.Integer, default=0)
        is_exemplar = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

        # Relationships
        tools = db.relationship("Tool", backref="substage", lazy="dynamic")

        @hybrid_property
        def tool_count(self):
            """Get the number of tools for this substage."""
            return self.tools.count() if hasattr(self.tools, "count") else 0

        def to_dict(self):
            """Convert substage to dictionary representation."""
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "stage_id": self.stage_id,
                "stage_name": self.stage.name if self.stage else None,
                "order": self.order,
                "is_exemplar": self.is_exemplar,
                "tool_count": self.tool_count,
                "created_at": self.created_at.isoformat() if self.created_at else None,
            }

    class ToolCategory(db.Model):
        """
        Tool categories for classification within stages.
        """

        __tablename__ = "tool_categories"

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False, index=True)
        description = db.Column(db.Text)
        stage_id = db.Column(
            db.Integer, db.ForeignKey("lifecycle_stages.id"), nullable=False
        )
        order = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

        # Relationships
        tools = db.relationship("Tool", backref="category", lazy="dynamic")

        @hybrid_property
        def tool_count(self):
            """Get the number of tools in this category."""
            return self.tools.count() if hasattr(self.tools, "count") else 0

        def to_dict(self):
            """Convert category to dictionary representation."""
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "stage_id": self.stage_id,
                "stage_name": self.stage.name if self.stage else None,
                "order": self.order,
                "tool_count": self.tool_count,
                "created_at": self.created_at.isoformat() if self.created_at else None,
            }

    class Tool(db.Model):
        """
        Enhanced tool model with MaLDReTH classifications.
        """

        __tablename__ = "tools"

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False, index=True)
        description = db.Column(db.Text)
        url = db.Column(db.String(500))
        provider = db.Column(db.String(200), index=True)
        tool_type = db.Column(db.String(200), index=True)
        source_type = db.Column(db.String(20), default="unknown")
        scope = db.Column(db.String(100), default="generic")
        is_interoperable = db.Column(db.Boolean, default=False)
        characteristics = db.Column(db.Text)
        stage_id = db.Column(
            db.Integer, db.ForeignKey("lifecycle_stages.id"), nullable=False
        )
        substage_id = db.Column(db.Integer, db.ForeignKey("lifecycle_substages.id"))
        category_id = db.Column(db.Integer, db.ForeignKey("tool_categories.id"))
        is_featured = db.Column(db.Boolean, default=False)
        usage_count = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        updated_at = db.Column(
            db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

        @classmethod
        def search(
            cls,
            query,
            stage_id=None,
            category_id=None,
            source_type=None,
            is_interoperable=None,
            limit=50,
        ):
            """Advanced tool search with filters."""
            q = cls.query

            if query:
                q = q.filter(
                    or_(
                        cls.name.ilike(f"%{query}%"),
                        cls.description.ilike(f"%{query}%"),
                        cls.provider.ilike(f"%{query}%"),
                    )
                )

            if stage_id:
                q = q.filter(cls.stage_id == stage_id)

            if category_id:
                q = q.filter(cls.category_id == category_id)

            if source_type:
                q = q.filter(cls.source_type == source_type)

            if is_interoperable is not None:
                q = q.filter(cls.is_interoperable == is_interoperable)

            return q.order_by(cls.usage_count.desc(), cls.name).limit(limit)

        def to_dict(self, include_relationships=False):
            """Convert tool to dictionary representation."""
            data = {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "url": self.url,
                "provider": self.provider,
                "tool_type": self.tool_type,
                "source_type": self.source_type,
                "scope": self.scope,
                "is_interoperable": self.is_interoperable,
                "characteristics": self.characteristics,
                "stage_id": self.stage_id,
                "substage_id": self.substage_id,
                "category_id": self.category_id,
                "is_featured": self.is_featured,
                "usage_count": self.usage_count,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            }

            if include_relationships:
                data.update(
                    {
                        "stage_name": self.stage.name if self.stage else None,
                        "substage_name": self.substage.name if self.substage else None,
                        "category_name": self.category.name if self.category else None,
                    }
                )

            return data

    class StageConnection(db.Model):
        """
        Connections between lifecycle stages.
        """

        __tablename__ = "stage_connections"

        id = db.Column(db.Integer, primary_key=True)
        from_stage_id = db.Column(
            db.Integer, db.ForeignKey("lifecycle_stages.id"), nullable=False
        )
        to_stage_id = db.Column(
            db.Integer, db.ForeignKey("lifecycle_stages.id"), nullable=False
        )
        connection_type = db.Column(db.String(50), default="normal", index=True)
        description = db.Column(db.Text)
        weight = db.Column(db.Float, default=1.0)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

        # Relationships
        from_stage = db.relationship("LifecycleStage", foreign_keys=[from_stage_id])
        to_stage = db.relationship("LifecycleStage", foreign_keys=[to_stage_id])

        def to_dict(self):
            """Convert to dictionary representation."""
            return {
                "id": self.id,
                "from_stage_id": self.from_stage_id,
                "to_stage_id": self.to_stage_id,
                "from_stage_name": self.from_stage.name if self.from_stage else None,
                "to_stage_name": self.to_stage.name if self.to_stage else None,
                "connection_type": self.connection_type,
                "description": self.description,
                "weight": self.weight,
                "is_active": self.is_active,
                "created_at": self.created_at.isoformat() if self.created_at else None,
            }
