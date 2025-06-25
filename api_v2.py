"""
Enhanced API endpoints for Phase 2 MaLDReTH integration.

This module provides RESTful API endpoints for accessing lifecycle stages,
tools, interactions, and visualization data with advanced filtering and search capabilities.
"""

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import or_, func
import logging

# Create blueprint for API v2
api_v2_bp = Blueprint("api_v2", __name__, url_prefix="/api/v2")

# Configure logging
logger = logging.getLogger(__name__)


def get_models():
    """
    Lazy import models to avoid circular imports.
    This function imports models only when needed.
    """
    from models_phase2 import (
        LifecycleStage,
        LifecycleSubstage,
        ToolCategory,
        Tool,
        Interaction,
        InteractionTool,
        StageConnection,
    )

    return {
        "LifecycleStage": LifecycleStage,
        "LifecycleSubstage": LifecycleSubstage,
        "ToolCategory": ToolCategory,
        "Tool": Tool,
        "Interaction": Interaction,
        "InteractionTool": InteractionTool,
        "StageConnection": StageConnection,
    }


def get_db():
    """Get database instance from current app context."""
    return current_app.extensions["sqlalchemy"]


@api_v2_bp.route("/stages", methods=["GET"])
def get_enhanced_stages():
    """
    Get all lifecycle stages with substages and tool counts.

    Query Parameters:
        include_substages (bool): Include substage information
        include_tools (bool): Include tool counts
        include_interactions (bool): Include interaction counts

    Returns:
        JSON array of stage objects with requested information
    """
    try:
        models = get_models()
        LifecycleStage = models["LifecycleStage"]
        LifecycleSubstage = models["LifecycleSubstage"]
        Tool = models["Tool"]

        include_substages = (
            request.args.get("include_substages", "true").lower() == "true"
        )
        include_tools = request.args.get("include_tools", "true").lower() == "true"
        include_interactions = (
            request.args.get("include_interactions", "false").lower() == "true"
        )

        stages = LifecycleStage.query.order_by(LifecycleStage.order).all()

        result = []
        for stage in stages:
            stage_data = {
                "id": stage.id,
                "name": stage.name,
                "description": stage.description,
                "maldreth_description": stage.maldreth_description,
                "order": stage.order,
                "color_code": stage.color_code,
                "icon": stage.icon,
            }

            if include_substages:
                stage_data["substages"] = [
                    {
                        "id": substage.id,
                        "name": substage.name,
                        "description": substage.description,
                        "order": substage.order,
                        "is_exemplar": substage.is_exemplar,
                        "tool_count": substage.tools.count(),
                    }
                    for substage in stage.substages.order_by(LifecycleSubstage.order)
                ]

            if include_tools:
                stage_data["tool_count"] = Tool.query.filter_by(
                    stage_id=stage.id
                ).count()
                stage_data["category_count"] = stage.tool_categories.count()

            if include_interactions:
                stage_data["interaction_counts"] = {
                    "as_source": stage.interactions_as_source.count(),
                    "as_target": stage.interactions_as_target.count(),
                }

            result.append(stage_data)

        return jsonify({"status": "success", "data": result, "count": len(result)}), 200

    except Exception as e:
        logger.error(f"Error fetching enhanced stages: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to fetch stages"}), 500


@api_v2_bp.route("/stages/<int:stage_id>/tools", methods=["GET"])
def get_stage_tools(stage_id):
    """
    Get all tools for a specific stage with filtering options.

    Path Parameters:
        stage_id (int): ID of the lifecycle stage

    Query Parameters:
        category_id (int): Filter by tool category
        source_type (str): Filter by source type (open, closed, freemium)
        scope (str): Filter by scope (Generic, Disciplinary)
        is_interoperable (bool): Filter by interoperability
        substage_id (int): Filter by substage
        page (int): Page number for pagination
        per_page (int): Items per page (default: 20, max: 100)

    Returns:
        JSON object with tools and pagination information
    """
    try:
        models = get_models()
        LifecycleStage = models["LifecycleStage"]
        Tool = models["Tool"]

        # Verify stage exists
        stage = LifecycleStage.query.get_or_404(stage_id)

        # Build query
        query = Tool.query.filter_by(stage_id=stage_id)

        # Apply filters
        category_id = request.args.get("category_id", type=int)
        if category_id:
            query = query.filter_by(category_id=category_id)

        source_type = request.args.get("source_type")
        if source_type:
            query = query.filter_by(source_type=source_type)

        scope = request.args.get("scope")
        if scope:
            query = query.filter_by(scope=scope)

        is_interoperable = request.args.get("is_interoperable")
        if is_interoperable is not None:
            query = query.filter_by(is_interoperable=is_interoperable.lower() == "true")

        substage_id = request.args.get("substage_id", type=int)
        if substage_id:
            query = query.filter_by(substage_id=substage_id)

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        tools = []
        for tool in pagination.items:
            tool_data = {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "url": tool.url,
                "provider": tool.provider,
                "tool_type": tool.tool_type,
                "source_type": tool.source_type,
                "scope": tool.scope,
                "is_interoperable": tool.is_interoperable,
                "characteristics": tool.characteristics,
                "category": (
                    {"id": tool.category.id, "name": tool.category.name}
                    if tool.category
                    else None
                ),
                "substage": (
                    {"id": tool.substage.id, "name": tool.substage.name}
                    if tool.substage
                    else None
                ),
            }
            tools.append(tool_data)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {
                        "stage": {"id": stage.id, "name": stage.name},
                        "tools": tools,
                        "pagination": {
                            "page": page,
                            "per_page": per_page,
                            "total": pagination.total,
                            "pages": pagination.pages,
                            "has_prev": pagination.has_prev,
                            "has_next": pagination.has_next,
                        },
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error fetching tools for stage {stage_id}: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to fetch tools"}), 500


@api_v2_bp.route("/tools/search", methods=["GET"])
def search_tools():
    """
    Advanced tool search with multiple filter options.

    Query Parameters:
        q (str): Search query for tool name, description, or provider
        stage_ids (str): Comma-separated list of stage IDs
        category_ids (str): Comma-separated list of category IDs
        source_types (str): Comma-separated list of source types
        scopes (str): Comma-separated list of scopes
        is_interoperable (bool): Filter by interoperability
        sort_by (str): Sort field (name, provider, stage)
        sort_order (str): Sort order (asc, desc)
        page (int): Page number
        per_page (int): Items per page

    Returns:
        JSON object with search results and pagination
    """
    try:
        models = get_models()
        Tool = models["Tool"]
        LifecycleStage = models["LifecycleStage"]
        db = get_db()

        # Base query
        query = Tool.query

        # Text search
        search_query = request.args.get("q", "").strip()
        if search_query:
            search_filter = or_(
                Tool.name.ilike(f"%{search_query}%"),
                Tool.description.ilike(f"%{search_query}%"),
                Tool.provider.ilike(f"%{search_query}%"),
                Tool.tool_type.ilike(f"%{search_query}%"),
            )
            query = query.filter(search_filter)

        # Stage filter
        stage_ids = request.args.get("stage_ids")
        if stage_ids:
            stage_id_list = [int(id) for id in stage_ids.split(",")]
            query = query.filter(Tool.stage_id.in_(stage_id_list))

        # Category filter
        category_ids = request.args.get("category_ids")
        if category_ids:
            category_id_list = [int(id) for id in category_ids.split(",")]
            query = query.filter(Tool.category_id.in_(category_id_list))

        # Source type filter
        source_types = request.args.get("source_types")
        if source_types:
            source_type_list = source_types.split(",")
            query = query.filter(Tool.source_type.in_(source_type_list))

        # Scope filter
        scopes = request.args.get("scopes")
        if scopes:
            scope_list = scopes.split(",")
            query = query.filter(Tool.scope.in_(scope_list))

        # Interoperability filter
        is_interoperable = request.args.get("is_interoperable")
        if is_interoperable is not None:
            query = query.filter_by(is_interoperable=is_interoperable.lower() == "true")

        # Sorting
        sort_by = request.args.get("sort_by", "name")
        sort_order = request.args.get("sort_order", "asc")

        if sort_by == "name":
            order_column = Tool.name
        elif sort_by == "provider":
            order_column = Tool.provider
        elif sort_by == "stage":
            query = query.join(LifecycleStage)
            order_column = LifecycleStage.order
        else:
            order_column = Tool.name

        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column)

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Format results
        tools = []
        for tool in pagination.items:
            tool_data = {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "url": tool.url,
                "provider": tool.provider,
                "tool_type": tool.tool_type,
                "source_type": tool.source_type,
                "scope": tool.scope,
                "is_interoperable": tool.is_interoperable,
                "stage": (
                    {
                        "id": tool.stage.id,
                        "name": tool.stage.name,
                        "color_code": tool.stage.color_code,
                    }
                    if tool.stage
                    else None
                ),
                "category": (
                    {"id": tool.category.id, "name": tool.category.name}
                    if tool.category
                    else None
                ),
            }
            tools.append(tool_data)

        # Get aggregations for filters
        aggregations = {
            "stages": db.session.query(
                LifecycleStage.id,
                LifecycleStage.name,
                func.count(Tool.id).label("count"),
            )
            .join(Tool)
            .group_by(LifecycleStage.id)
            .all(),
            "source_types": db.session.query(
                Tool.source_type, func.count(Tool.id).label("count")
            )
            .filter(Tool.source_type.isnot(None))
            .group_by(Tool.source_type)
            .all(),
            "scopes": db.session.query(Tool.scope, func.count(Tool.id).label("count"))
            .filter(Tool.scope.isnot(None))
            .group_by(Tool.scope)
            .all(),
        }

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {
                        "tools": tools,
                        "pagination": {
                            "page": page,
                            "per_page": per_page,
                            "total": pagination.total,
                            "pages": pagination.pages,
                            "has_prev": pagination.has_prev,
                            "has_next": pagination.has_next,
                        },
                        "aggregations": {
                            "stages": [
                                {"id": s[0], "name": s[1], "count": s[2]}
                                for s in aggregations["stages"]
                            ],
                            "source_types": [
                                {"type": s[0], "count": s[1]}
                                for s in aggregations["source_types"]
                            ],
                            "scopes": [
                                {"scope": s[0], "count": s[1]}
                                for s in aggregations["scopes"]
                            ],
                        },
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error searching tools: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to search tools"}), 500


@api_v2_bp.route("/interactions/recommend-tools", methods=["POST"])
def recommend_tools():
    """
    Recommend tools based on interaction characteristics.

    Request Body:
        {
            "source_stage_id": int,
            "target_stage_id": int,
            "interaction_type": str,
            "source_infrastructure": str,
            "target_infrastructure": str
        }

    Returns:
        JSON object with recommended tools for the interaction
    """
    try:
        models = get_models()
        Tool = models["Tool"]

        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        source_stage_id = data.get("source_stage_id")
        target_stage_id = data.get("target_stage_id")
        interaction_type = data.get("interaction_type")

        recommendations = {
            "source_tools": [],
            "target_tools": [],
            "facilitator_tools": [],
        }

        # Get tools from source stage that support interoperability
        if source_stage_id:
            source_tools = (
                Tool.query.filter_by(stage_id=source_stage_id, is_interoperable=True)
                .limit(5)
                .all()
            )

            recommendations["source_tools"] = [
                {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "reason": "Supports data interoperability",
                }
                for tool in source_tools
            ]

        # Get tools from target stage
        if target_stage_id:
            target_tools = Tool.query.filter_by(stage_id=target_stage_id).limit(5).all()

            recommendations["target_tools"] = [
                {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "reason": "Compatible with target stage",
                }
                for tool in target_tools
            ]

        # Get facilitator tools based on interaction type
        if interaction_type == "data_transfer":
            # Recommend ETL tools
            etl_tools = Tool.query.filter(Tool.tool_type.ilike("%ETL%")).limit(3).all()

            recommendations["facilitator_tools"].extend(
                [
                    {
                        "id": tool.id,
                        "name": tool.name,
                        "description": tool.description,
                        "reason": "ETL capability for data transfer",
                    }
                    for tool in etl_tools
                ]
            )

        return jsonify({"status": "success", "data": recommendations}), 200

    except Exception as e:
        logger.error(f"Error recommending tools: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to recommend tools"}), 500


@api_v2_bp.route("/visualization/network", methods=["GET"])
def get_network_data():
    """
    Get data for network visualization of stages, tools, and interactions.

    Query Parameters:
        include_tools (bool): Include tools in the network
        include_interactions (bool): Include interactions
        stage_ids (str): Comma-separated list of stage IDs to include

    Returns:
        JSON object with nodes and edges for network visualization
    """
    try:
        models = get_models()
        LifecycleStage = models["LifecycleStage"]
        Tool = models["Tool"]
        StageConnection = models["StageConnection"]
        Interaction = models["Interaction"]

        include_tools = request.args.get("include_tools", "false").lower() == "true"
        include_interactions = (
            request.args.get("include_interactions", "true").lower() == "true"
        )
        stage_ids = request.args.get("stage_ids")

        nodes = []
        edges = []

        # Build stage query
        stage_query = LifecycleStage.query
        if stage_ids:
            stage_id_list = [int(id) for id in stage_ids.split(",")]
            stage_query = stage_query.filter(LifecycleStage.id.in_(stage_id_list))

        stages = stage_query.all()

        # Add stage nodes
        for stage in stages:
            nodes.append(
                {
                    "id": f"stage_{stage.id}",
                    "label": stage.name,
                    "type": "stage",
                    "color": stage.color_code,
                    "icon": stage.icon,
                    "data": {
                        "description": stage.description,
                        "tool_count": Tool.query.filter_by(stage_id=stage.id).count(),
                    },
                }
            )

        # Add stage connections
        connections = StageConnection.query.all()
        for conn in connections:
            if not stage_ids or (
                str(conn.from_stage_id) in stage_ids.split(",")
                and str(conn.to_stage_id) in stage_ids.split(",")
            ):
                edges.append(
                    {
                        "id": f"conn_{conn.id}",
                        "source": f"stage_{conn.from_stage_id}",
                        "target": f"stage_{conn.to_stage_id}",
                        "type": conn.connection_type,
                        "label": conn.connection_type,
                    }
                )

        # Add tools if requested
        if include_tools:
            tool_query = Tool.query
            if stage_ids:
                tool_query = tool_query.filter(Tool.stage_id.in_(stage_id_list))

            tools = tool_query.limit(50).all()  # Limit for performance

            for tool in tools:
                nodes.append(
                    {
                        "id": f"tool_{tool.id}",
                        "label": tool.name,
                        "type": "tool",
                        "color": "#95a5a6",
                        "data": {
                            "provider": tool.provider,
                            "source_type": tool.source_type,
                            "is_interoperable": tool.is_interoperable,
                        },
                    }
                )

                # Connect tool to its stage
                edges.append(
                    {
                        "id": f"tool_stage_{tool.id}",
                        "source": f"stage_{tool.stage_id}",
                        "target": f"tool_{tool.id}",
                        "type": "contains",
                        "style": "dashed",
                    }
                )

        # Add interactions if requested
        if include_interactions:
            interaction_query = Interaction.query
            if stage_ids:
                stage_id_list = [int(id) for id in stage_ids.split(",")]
                interaction_query = interaction_query.filter(
                    or_(
                        Interaction.source_stage_id.in_(stage_id_list),
                        Interaction.target_stage_id.in_(stage_id_list),
                    )
                )

            interactions = interaction_query.limit(30).all()  # Limit for performance

            for interaction in interactions:
                # Add interaction node
                nodes.append(
                    {
                        "id": f"interaction_{interaction.id}",
                        "label": interaction.interaction_type,
                        "type": "interaction",
                        "color": "#e74c3c",
                        "data": {
                            "description": interaction.description,
                            "priority": interaction.priority,
                            "complexity": interaction.complexity,
                        },
                    }
                )

                # Connect interaction to stages
                if interaction.source_stage_id:
                    edges.append(
                        {
                            "id": f"int_source_{interaction.id}",
                            "source": f"stage_{interaction.source_stage_id}",
                            "target": f"interaction_{interaction.id}",
                            "type": "interaction_source",
                            "style": "dotted",
                        }
                    )

                if interaction.target_stage_id:
                    edges.append(
                        {
                            "id": f"int_target_{interaction.id}",
                            "source": f"interaction_{interaction.id}",
                            "target": f"stage_{interaction.target_stage_id}",
                            "type": "interaction_target",
                            "style": "dotted",
                        }
                    )

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {
                        "nodes": nodes,
                        "edges": edges,
                        "statistics": {
                            "node_count": len(nodes),
                            "edge_count": len(edges),
                            "stage_count": len(
                                [n for n in nodes if n["type"] == "stage"]
                            ),
                            "tool_count": len(
                                [n for n in nodes if n["type"] == "tool"]
                            ),
                            "interaction_count": len(
                                [n for n in nodes if n["type"] == "interaction"]
                            ),
                        },
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting network data: {str(e)}")
        return (
            jsonify({"status": "error", "message": "Failed to get network data"}),
            500,
        )


@api_v2_bp.route("/stats/dashboard", methods=["GET"])
def get_dashboard_stats():
    """
    Get statistics for the dashboard overview.

    Returns:
        JSON object with various statistics and metrics
    """
    try:
        models = get_models()
        db = get_db()

        LifecycleStage = models["LifecycleStage"]
        LifecycleSubstage = models["LifecycleSubstage"]
        Tool = models["Tool"]
        Interaction = models["Interaction"]
        ToolCategory = models["ToolCategory"]

        stats = {
            "total_stages": LifecycleStage.query.count(),
            "total_substages": LifecycleSubstage.query.count(),
            "total_tools": Tool.query.count(),
            "total_interactions": Interaction.query.count(),
            "total_categories": ToolCategory.query.count(),
            "tools_by_source_type": db.session.query(
                Tool.source_type, func.count(Tool.id).label("count")
            )
            .filter(Tool.source_type.isnot(None))
            .group_by(Tool.source_type)
            .all(),
            "tools_by_scope": db.session.query(
                Tool.scope, func.count(Tool.id).label("count")
            )
            .filter(Tool.scope.isnot(None))
            .group_by(Tool.scope)
            .all(),
            "interoperable_tools": Tool.query.filter_by(is_interoperable=True).count(),
            "interactions_by_priority": db.session.query(
                Interaction.priority, func.count(Interaction.id).label("count")
            )
            .group_by(Interaction.priority)
            .all(),
            "interactions_by_complexity": db.session.query(
                Interaction.complexity, func.count(Interaction.id).label("count")
            )
            .group_by(Interaction.complexity)
            .all(),
            "top_tool_providers": db.session.query(
                Tool.provider, func.count(Tool.id).label("count")
            )
            .filter(Tool.provider.isnot(None))
            .group_by(Tool.provider)
            .order_by(func.count(Tool.id).desc())
            .limit(10)
            .all(),
        }

        # Format the response
        formatted_stats = {
            "totals": {
                "stages": stats["total_stages"],
                "substages": stats["total_substages"],
                "tools": stats["total_tools"],
                "interactions": stats["total_interactions"],
                "categories": stats["total_categories"],
                "interoperable_tools": stats["interoperable_tools"],
            },
            "distributions": {
                "tools_by_source_type": [
                    {"type": s[0], "count": s[1]} for s in stats["tools_by_source_type"]
                ],
                "tools_by_scope": [
                    {"scope": s[0], "count": s[1]} for s in stats["tools_by_scope"]
                ],
                "interactions_by_priority": [
                    {"priority": p[0], "count": p[1]}
                    for p in stats["interactions_by_priority"]
                ],
                "interactions_by_complexity": [
                    {"complexity": c[0], "count": c[1]}
                    for c in stats["interactions_by_complexity"]
                ],
            },
            "top_providers": [
                {"provider": p[0], "tool_count": p[1]}
                for p in stats["top_tool_providers"]
            ],
        }

        return jsonify({"status": "success", "data": formatted_stats}), 200

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return (
            jsonify(
                {"status": "error", "message": "Failed to get dashboard statistics"}
            ),
            500,
        )
