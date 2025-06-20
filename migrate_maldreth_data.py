#!/usr/bin/env python3
"""
MaLDReTH Data Migration Script

This script migrates data from MaLDReTH 1 repositories into the enhanced
Phase 2 database structure, consolidating tools, substages, and lifecycle
information from multiple sources.

Usage:
    python migrate_maldreth_data.py --source all
    python migrate_maldreth_data.py --source maldreth-viz
    python migrate_maldreth_data.py --source maldreth-lf
    python migrate_maldreth_data.py --dry-run
"""

import os
import sys
import sqlite3
import pandas as pd
import requests
import json
import argparse
import logging
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models_phase2 import (
    LifecycleStage, LifecycleSubstage, ToolCategory, Tool, 
    Interaction, StageConnection, init_maldreth_data
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers
