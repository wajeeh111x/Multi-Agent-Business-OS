"""Application package for the backend services."""
import sys
from pathlib import Path

# Ensure the backend directory is in sys.path for proper imports
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

