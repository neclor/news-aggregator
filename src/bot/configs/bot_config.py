import os
from pathlib import Path

from dotenv import load_dotenv


_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(_ROOT / "configs" / ".env")


API_ID: int = int(os.environ.get("TG_API_ID", "0"))
API_HASH: str = os.environ.get("TG_API_HASH", "")
BOT_TOKEN: str = os.environ.get("TG_BOT_TOKEN", "")


API_BASE: str = os.environ.get("API_BASE", "http://localhost:8000")
SESSION_PATH: Path = _ROOT / "data" / "bot_session"
DATA_FILE: Path = _ROOT / "data" / "bot_data.json"
POLL_INTERVAL: int = 600
