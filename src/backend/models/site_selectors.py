from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SiteSelectors:
    articles: str
    title: str
    url: str
    text: str = ""
