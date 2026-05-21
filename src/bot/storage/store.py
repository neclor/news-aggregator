import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class _Entry(TypedDict):
    feed_id: str
    last_seen: str


@dataclass
class Subscription:
    feed_id: str
    last_seen: datetime


class Store:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[str, _Entry] = {}
        if path.exists():
            self._data = json.loads(path.read_text(encoding="utf-8"))


    def get(self, chat_id: int) -> Subscription | None:
        entry = self._data.get(str(chat_id))
        if entry is None:
            return None
        return Subscription(
            feed_id=entry["feed_id"],
            last_seen=datetime.fromisoformat(entry["last_seen"]),
        )


    def save(self, chat_id: int, feed_id: str, last_seen: datetime) -> None:
        self._data[str(chat_id)] = {
            "feed_id": feed_id,
            "last_seen": last_seen.isoformat(),
        }
        self._flush()


    def update_last_seen(self, chat_id: int, ts: datetime) -> None:
        if str(chat_id) in self._data:
            self._data[str(chat_id)]["last_seen"] = ts.isoformat()
            self._flush()


    def remove(self, chat_id: int) -> None:
        self._data.pop(str(chat_id), None)
        self._flush()


    def all(self) -> list[tuple[int, Subscription]]:
        return [
            (int(k), Subscription(
                feed_id=v["feed_id"],
                last_seen=datetime.fromisoformat(v["last_seen"]),
            ))
            for k, v in self._data.items()
        ]


    def _flush(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
