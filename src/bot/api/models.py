from dataclasses import dataclass
from datetime import datetime


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
