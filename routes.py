"""
Routes module for the Research Data Lifecycle Visualization application.

This module defines all the HTTP endpoints and their handlers for the Flask application,
including API endpoints for data retrieval and web routes for serving the visualization.
"""

import logging

from flask import (Blueprint, jsonify, render_template, request,
                   send_from_directory)

from app import db
from models import LifecycleConnection, LifecycleStage, Tool, ToolCategory

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Render the main visualization page.

    Returns:
        str: Rendered HTML template for the main visualization
    """
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return jsonify({"error": "Failed to load main page"}), 500


@main_bp.route("/curator")
def curator():
    """
    Render the curator/admin interface for managing tools and stages.

    Returns:
        str: Rendered HTML template for the curator interface
    """
    try:
        stages = LifecycleStage.query.order_by(LifecycleStage.order).all()
        return render_template("curator.html", stages=stages)
    except Exception as e:
        logger.error(f"Error rendering curator page: {e}")
        return jsonify({"error": "Failed to load curator page"}), 500


# API Routes for lifecycle data
@main_bp.route("/api/lifecycle", methods=["GET"])
def get_lifecycle():
    """
    Retrieve all lifecycle stages with their descriptions.

    Returns:
        flask.Response: JSON response with lifecycle stages
    """
    try:
        stages = LifecycleStage.query.order_by(LifecycleStage.order).all()
        return jsonify(
            [
                {
                    "id": stage.id,
                    "name": stage.name,
                    "description": stage.description,
                    "order": stage.order,
                }
                for stage in stages
            ]
        )
    except Exception as e:
        logger.error(f"Error retrieving lifecycle data: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/api/layout/<view_mode>", methods=["GET"])
def get_layout(view_mode):
    """
    Get the layout configuration for a specific view mode.

    Args:
        view_mode (str): The view mode ('circular', 'linear', etc.)

    Returns:
        flask.Response: JSON response with layout configuration
    """
    try:
        stages = LifecycleStage.query.order_by(LifecycleStage.order).all()
        connections = LifecycleConnection.query.all()

        if not stages:
            logger.warning(f"No stages found for view mode: {view_mode}")
            return jsonify({"error": "No stages found"}), 404

        layout = {
            "stages": [
                {
                    "id": stage.id,
                    "name": stage.name,
                    "description": stage.description,
                    "x": None,  # Will be calculated on frontend based on view_mode
                    "y": None,
                }
                for stage in stages
            ],
            "connections": [
                {
                    "from": conn.from_stage.name,
                    "to": conn.to_stage.name,
                    "type": conn.connection_type,
                }
                for conn in connections
                if conn.from_stage and conn.to_stage
            ],
        }
        return jsonify(layout)
    except Exception as e:
        logger.error(f"Error getting layout for view mode {view_mode}: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/api/connections", methods=["GET"])
def get_connections():
    """
    Retrieve all connections between lifecycle stages.

    Returns:
        flask.Response: JSON response with connections
    """
    try:
        connections = LifecycleConnection.query.all()
        return jsonify(
            [
                {
                    "from": conn.from_stage.name if conn.from_stage else None,
                    "to": conn.to_stage.name if conn.to_stage else None,
                    "type": conn.connection_type,
                }
                for conn in connections
            ]
        )
    except Exception as e:
        logger.error(f"Error retrieving connections: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/api/stage/<int:stage_id>/categories", methods=["GET"])
def get_categories(stage_id):
    """
    Get tool categories for a specific stage.

    Args:
        stage_id (int): The ID of the lifecycle stage

    Returns:
        flask.Response: JSON response with tool categories
    """
    try:
        LifecycleStage.query.get_or_404(stage_id)
        categories = ToolCategory.query.filter_by(stage_id=stage_id).all()

        return jsonify(
            [
                {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "tools_count": category.tools.count(),
                }
                for category in categories
            ]
        )
    except Exception as e:
        logger.error(f"Error getting categories for stage {stage_id}: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/api/category/<int:category_id>/tools", methods=["GET"])
def get_tools(category_id):
    """
    Get tools for a specific category.

    Args:
        category_id (int): The ID of the tool category

    Returns:
        flask.Response: JSON response with tools
    """
    try:
        ToolCategory.query.get_or_404(category_id)
        tools = Tool.query.filter_by(category_id=category_id).all()

        return jsonify([tool.to_dict() for tool in tools])
    except Exception as e:
        logger.error(f"Error getting tools for category {category_id}: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/api/stages/<stage_name>/tools", methods=["GET"])
def get_tools_by_stage(stage_name):
    """
    Get all tools for a specific stage by stage name.

    Args:
        stage_name (str): Name of the lifecycle stage

    Returns:
        flask.Response: JSON response with tools grouped by category
    """
    try:
        stage = LifecycleStage.query.filter_by(name=stage_name).first_or_404()
        categories = ToolCategory.query.filter_by(stage_id=stage.id).all()

        result = {"stage": stage.to_dict(), "categories": []}

        for category in categories:
            tools = Tool.query.filter_by(category_id=category.id).all()
            result["categories"].append(
                {
                    "category": category.to_dict(),
                    "tools": [tool.to_dict() for tool in tools],
                }
            )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting tools for stage {stage_name}: {e}")
        return jsonify({"error": str(e)}), 500


# CRUD operations for curator interface
@main_bp.route("/api/stages", methods=["POST"])
def create_stage():
    """
    Create a new lifecycle stage.

    Returns:
        flask.Response: JSON response with created stage or error
    """
    try:
        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({"error": "Stage name is required"}), 400

        # Check if stage already exists
        existing = LifecycleStage.query.filter_by(name=data["name"]).first()
        if existing:
            return jsonify({"error": "Stage with this name already exists"}), 409

        stage = LifecycleStage(
            name=data["name"],
            description=data.get("description", ""),
            order=data.get("order", 999),
        )

        db.session.add(stage)
        db.session.commit()

        logger.info(f"Created new stage: {stage.name}")
        return jsonify(stage.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating stage: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/api/tools", methods=["POST"])
def create_tool():
    """
    Create a new tool.

    Returns:
        flask.Response: JSON response with created tool or error
    """
    try:
        data = request.get_json()

        required_fields = ["name", "category_id"]
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Name and category_id are required"}), 400

        # Verify category exists
        category = ToolCategory.query.get(data["category_id"])
        if not category:
            return jsonify({"error": "Category not found"}), 404

        tool = Tool(
            name=data["name"],
            description=data.get("description", ""),
            url=data.get("url", ""),
            provider=data.get("provider", ""),
            tool_type=data.get("tool_type", ""),
            source=data.get("source", ""),
            scope=data.get("scope", ""),
            is_interoperable=data.get("is_interoperable", False),
            category_id=data["category_id"],
        )

        db.session.add(tool)
        db.session.commit()

        logger.info(f"Created new tool: {tool.name}")
        return jsonify(tool.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating tool: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/api/tools/<int:tool_id>", methods=["PUT"])
def update_tool(tool_id):
    """
    Update an existing tool.

    Args:
        tool_id (int): ID of the tool to update

    Returns:
        flask.Response: JSON response with updated tool or error
    """
    try:
        tool = Tool.query.get_or_404(tool_id)
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update fields if provided
        updateable_fields = [
            "name",
            "description",
            "url",
            "provider",
            "tool_type",
            "source",
            "scope",
            "is_interoperable",
        ]

        for field in updateable_fields:
            if field in data:
                setattr(tool, field, data[field])

        db.session.commit()

        logger.info(f"Updated tool: {tool.name}")
        return jsonify(tool.to_dict())

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating tool {tool_id}: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/api/tools/<int:tool_id>", methods=["DELETE"])
def delete_tool(tool_id):
    """
    Delete a tool.

    Args:
        tool_id (int): ID of the tool to delete

    Returns:
        flask.Response: JSON response confirming deletion or error
    """
    try:
        tool = Tool.query.get_or_404(tool_id)
        tool_name = tool.name

        db.session.delete(tool)
        db.session.commit()

        logger.info(f"Deleted tool: {tool_name}")
        return jsonify({"message": f'Tool "{tool_name}" deleted successfully'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting tool {tool_id}: {e}")
        return jsonify({"error": str(e)}), 500


# Static file serving
@main_bp.route("/static/<path:filename>")
def serve_static(filename):
    """
    Serve static files.

    Args:
        filename (str): Path to the static file

    Returns:
        flask.Response: Static file response
    """
    try:
        return send_from_directory("static", filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return jsonify({"error": "File not found"}), 404


# Health check endpoint
@main_bp.route("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        flask.Response: JSON response with health status
    """
    try:
        # Simple database connectivity check
        stage_count = LifecycleStage.query.count()
        return jsonify(
            {"status": "healthy", "database": "connected", "stages_count": stage_count}
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return (
            jsonify(
                {"status": "unhealthy", "database": "disconnected", "error": str(e)}
            ),
            503,
        )
