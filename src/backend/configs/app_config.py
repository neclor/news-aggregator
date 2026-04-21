import os
from pathlib import Path

from dotenv import load_dotenv


_ROOT: Path = Path(__file__).parent.parent.parent.parent
_DATA_DIR: Path = _ROOT / "data"
load_dotenv(_ROOT / "configs" / ".env")


DB_PATH: Path = _DATA_DIR / "news.db"
FETCH_INTERVAL_SEC: int = 600


TG_SESSION_PATH: Path = _DATA_DIR / "backend_user_session"
TG_API_ID: int = int(os.environ.get("TG_API_ID", "0"))
TG_API_HASH: str = os.environ.get("TG_API_HASH", "")


TG_RECONNECT_DELAY: int = 60
