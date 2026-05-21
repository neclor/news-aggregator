import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BOT_DATA_PATH: Path = Path(os.getenv("BOT_DATA_PATH", "data/bot_data.json"))
BOT_POLL_INTERVAL: int = int(os.getenv("BOT_POLL_INTERVAL", "600"))

BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

TG_BOT_API_ID: int = int(os.getenv("TG_BOT_API_ID", "0"))
TG_BOT_API_HASH: str = os.getenv("TG_BOT_API_HASH", "")
TG_BOT_TOKEN: str = os.getenv("TG_BOT_TOKEN", "")
TG_BOT_SESSION_PATH: Path = Path(os.getenv("TG_BOT_SESSION_PATH", "data/bot_session"))
