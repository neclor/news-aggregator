from dataclasses import dataclass
from datetime import datetime

from backend.utils.url_utils import normalize_url


@dataclass(frozen=True, slots=True)
class NewsItem:
    source: str
    url: str
    title: str
    text: str
    published_at: datetime
    author: str | None = None
    is_read: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "url", normalize_url(self.url))
        object.__setattr__(self, "source", normalize_url(self.source))
