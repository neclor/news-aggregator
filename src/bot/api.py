from dataclasses import dataclass
from datetime import datetime

import httpx


@dataclass
class Feed:
    id: str
    name: str


@dataclass
class NewsItem:
    url: str
    source: str
    title: str
    text: str
    published_at: datetime


class ApiClient:
    def __init__(self, base_url: str, http: httpx.AsyncClient) -> None:
        self._base = base_url.rstrip("/")
        self._http = http


    async def get_feeds(self) -> list[Feed]:
        r = await self._http.get(f"{self._base}/feeds", timeout=10)
        r.raise_for_status()
        return [Feed(id=f["id"], name=f["name"]) for f in r.json()]


    async def get_news(self, feed_id: str, limit: int = 500) -> list[NewsItem]:
        r = await self._http.get(
            f"{self._base}/feeds/{feed_id}/news",
            params={"limit": limit, "all_time": "true"},
            timeout=10,
        )
        r.raise_for_status()
        return [
            NewsItem(
                url=item["url"],
                source=item["source"],
                title=item["title"],
                text=item.get("text") or "",
                published_at=datetime.fromisoformat(item["published_at"]),
            )
            for item in r.json()
        ]
