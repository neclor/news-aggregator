from dataclasses import dataclass, field
from datetime import timedelta
from uuid import UUID, uuid4

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
