import logging
from datetime import datetime, timezone

import httpx
from parsel import Selector
from urllib.parse import urljoin

from backend.utils.http_utils import random_user_agent_headers
from backend.models import NewsItem, SiteSelectors
from backend.core.aggregator.parsers.parser import Parser


logger: logging.Logger = logging.getLogger(__name__)


class SiteParser(Parser):
    def __init__(self, http: httpx.AsyncClient, url: str, selectors: SiteSelectors) -> None:
        self._http = http
        self._url = url
        self._selectors = selectors


    @property
    def url(self) -> str:
        return self._url


    async def fetch(self) -> list[NewsItem]:
        logger.debug("Fetching site: %s", self._url)
        response = await self._http.get(self._url, headers=random_user_agent_headers())
        response.raise_for_status()
        items = self._parse(response.text)
        logger.info("Fetched %d items from %s", len(items), self._url)
        return items


    def _parse(self, html: str) -> list[NewsItem]:
        sel = Selector(text=html)
        items = []
        for article in sel.css(self._selectors.articles):
            title = article.css(self._selectors.title).get(default="").strip()
            href = article.css(self._selectors.url).get(default="")
            text = article.css(self._selectors.text).get(default="").strip() if self._selectors.text else ""
            url = _resolve_url(self._url, href)
            if not url: continue

            items.append(NewsItem(
                source=self._url,
                url=url,
                title=title,
                text=text,
                published_at=datetime.now(timezone.utc),
                author=None,
            ))
        return items


def _resolve_url(base: str, href: str) -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return urljoin(base, href)
