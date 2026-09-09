import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


DB_PATH: Path = Path(os.getenv("DB_PATH", "data/news.db"))
FETCH_INTERVAL_SEC: int = int(os.getenv("FETCH_INTERVAL_SEC", "600"))
RETENTION_DAYS: int = int(os.getenv("RETENTION_DAYS", "60"))

TG_BACKEND_API_ID: int = int(os.getenv("TG_BACKEND_API_ID", "0"))
TG_BACKEND_API_HASH: str = os.getenv("TG_BACKEND_API_HASH", "")
TG_BACKEND_SESSION_PATH: Path = Path(os.getenv("TG_BACKEND_SESSION_PATH", "data/backend_session"))
TG_BACKEND_RECONNECT_DELAY: int = int(os.getenv("TG_BACKEND_RECONNECT_DELAY", "60"))
