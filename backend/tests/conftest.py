import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

# Force mock mode + disable network for deterministic, offline test runs,
# regardless of what's in the developer's local .env.
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["ZYNTH_ALLOW_NETWORK"] = "false"

from config import get_settings  # noqa: E402

get_settings.cache_clear()
