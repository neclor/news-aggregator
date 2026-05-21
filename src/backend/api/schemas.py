from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from backend.models import ParserType


class FeedIn(BaseModel):
    name: str
    sources: list[str] = []
    keywords: list[str] = []
    blacklist: list[str] = []
    max_age_hours: float | None = Field(default=None, gt=0)

    @field_validator('keywords', 'sources', 'blacklist', mode='before')
    @classmethod
    def deduplicate(cls, v: list[str]) -> list[str]:
        return list(dict.fromkeys(kw for kw in v if kw))


class FeedOut(BaseModel):
    id: UUID
    name: str
    sources: list[str]
    keywords: list[str]
    blacklist: list[str]
    max_age_hours: float | None


class NewsItemOut(BaseModel):
    url: str
    source: str
    title: str
    text: str
    published_at: datetime
    author: str | None
    is_read: bool


class SourceStat(BaseModel):
    source: str
    count: int


class DayStat(BaseModel):
    date: str
    count: int


class FeedStatsOut(BaseModel):
    total: int
    read: int
    unread: int
    by_source: list[SourceStat]
    daily: list[DayStat]


class MarkReadIn(BaseModel):
    url: str


class SiteSelectorsIn(BaseModel):
    articles: str
    title: str
    url: str
    text: str = ""


class SourceIn(BaseModel):
    url: str
    type: ParserType = "rss"
    selectors: SiteSelectorsIn | None = None


class SourceOut(BaseModel):
    url: str
    type: ParserType
