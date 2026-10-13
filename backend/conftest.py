"""Pytest configuration file.

This file automatically adds the backend directory to sys.path for proper imports.
"""
import sys
from pathlib import Path

# Add the backend directory to sys.path
backend_dir = str(Path(__file__).parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
