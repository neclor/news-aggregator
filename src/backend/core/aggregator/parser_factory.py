import httpx
from telethon import TelegramClient

from backend.core.aggregator.parsers import Parser, RssParser, SiteParser, TelegramParser
from backend.models import SourceConfig


class ParserFactory:
    def __init__(self, http: httpx.AsyncClient, tg_client: TelegramClient | None = None) -> None:
        self._http = http
        self._tg = tg_client


    def create(self, config: SourceConfig) -> Parser:
        match config.type:
            case "rss":
                return RssParser(self._http, config.url)
            case "telegram":
                if self._tg is None:
                    raise ValueError("TelegramClient is required for telegram sources")
                return TelegramParser(self._tg, config.url, config.limit)
            case "site":
                if config.selectors is None:
                    raise ValueError(f"SiteSelectors required for site source '{config.url}'")
                return SiteParser(self._http, config.url, config.selectors)
            case _:
                raise ValueError(f"Unknown source type: '{config.type}'")
