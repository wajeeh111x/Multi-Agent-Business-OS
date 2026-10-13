import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import settings

print(settings.DATABASE_URL)
print(settings.SECRET_KEY)
print(settings.OLLAMA_MODEL)