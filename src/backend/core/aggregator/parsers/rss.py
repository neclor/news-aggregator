import calendar
import logging
from datetime import datetime, timezone
from time import struct_time

import feedparser
import httpx

from backend.utils.http_utils import random_user_agent_headers
from backend.models import NewsItem
from backend.core.aggregator.parsers.parser import Parser


logger: logging.Logger = logging.getLogger(__name__)


class RssParser(Parser):
    def __init__(self, http: httpx.AsyncClient, url: str) -> None:
        self._http = http
        self._url = url


    @property
    def url(self) -> str:
        return self._url


    async def fetch(self) -> list[NewsItem]:
        logger.debug("Fetching RSS feed: %s", self._url)
        response = await self._http.get(self._url, headers=random_user_agent_headers())
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        items = [self._to_news_item(e) for e in feed.entries if e.get("link")]
        logger.info("Fetched %d items from %s", len(items), self._url)
        return items


    def _to_news_item(self, entry) -> NewsItem:
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        return NewsItem(
            source=self._url,
            url=entry.get("link", ""),
            title=entry.get("title", ""),
            text=entry.get("summary", ""),
            published_at=_to_datetime(published),
            author=entry.get("author"),
        )


def _to_datetime(value: struct_time | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(calendar.timegm(value), tz=timezone.utc)
