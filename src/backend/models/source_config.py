from dataclasses import dataclass

from backend.models.parser_type import ParserType
from backend.models.site_selectors import SiteSelectors
from backend.utils.url_utils import normalize_url


DEFAULT_LIMIT: int = 50


@dataclass
class SourceConfig:
    url: str
    type: ParserType = "rss"
    selectors: SiteSelectors | None = None
    limit: int = DEFAULT_LIMIT

    def __post_init__(self) -> None:
        self.url = normalize_url(self.url)
