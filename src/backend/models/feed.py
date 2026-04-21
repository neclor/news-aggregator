import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from backend.models.news_item import NewsItem
from backend.utils.url_utils import normalize_url


@dataclass
class Feed:
    name: str
    id: UUID = field(default_factory=uuid4)
    sources: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    max_age: timedelta | None = None


    def __post_init__(self) -> None:
        self.sources = [normalize_url(url) for url in self.sources]
        self.keywords = [kw for kw in self.keywords if kw.strip()]


    def matches(self, item: NewsItem) -> bool:
        if not self.within_max_age(item.published_at):
            return False
        if not self.keywords:
            return True
        haystack = f"{item.title} {item.text}".lower()
        return any(re.search(r'\b' + re.escape(kw.lower()) + r'\b', haystack) for kw in self.keywords)

    def within_max_age(self, published_at: datetime) -> bool:
        if self.max_age is None:
            return True
        return datetime.now(timezone.utc) - published_at <= self.max_age
