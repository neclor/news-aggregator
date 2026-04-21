from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceCount:
    source: str
    count: int


@dataclass(frozen=True, slots=True)
class DayCount:
    date: str
    count: int


@dataclass
class FeedStats:
    total: int
    read: int
    unread: int
    by_source: list[SourceCount]
    daily: list[DayCount]
