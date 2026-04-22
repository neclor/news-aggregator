import logging
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from backend.infra.aggregator import aggregator
from backend.infra.aggregator.parser_factory import ParserFactory
from backend.models.source_config import SourceConfig
from backend.models.feed import Feed
from backend.models.news_item import NewsItem
from backend.infra.db.feed_repo import FeedRepository
from backend.infra.db.news_repo import NewsRepository
from backend.models.feed_stats import FeedStats
from backend.infra.db.source_repo import SourceRepository
from backend.infra.aggregator.parsers.parser import Parser
from backend.services.telegram_connection import TelegramConnection


logger: logging.Logger = logging.getLogger(__name__)


class NewsService:
    def __init__(
        self,
        factory: ParserFactory,
        news_repo: NewsRepository,
        feed_repo: FeedRepository,
        source_repo: SourceRepository,
        tg: TelegramConnection | None = None,
    ) -> None:
        self._factory = factory
        self._news_repo = news_repo
        self._feed_repo = feed_repo
        self._source_repo = source_repo
        self._tg = tg


    async def add_feed(self, feed: Feed) -> None:
        await self._auto_register_sources(feed.sources)
        await self._feed_repo.save(feed)
        await self._relink_feed(feed)
        logger.info("Feed saved: %s ('%s')", feed.id, feed.name)


    async def _auto_register_sources(self, urls: list[str]) -> None:
        existing = {s.url for s in await self._source_repo.get_all()}
        for url in urls:
            if url in existing:
                continue
            inferred: Literal["telegram", "rss"] = "telegram" if (url.startswith("@") or "t.me/" in url) else "rss"
            await self.add_source(SourceConfig(url=url, type=inferred))
            logger.info("Auto-registered source: %s (%s)", url, inferred)


    async def _relink_feed(self, feed: Feed) -> None:
        items = await self._news_repo.get_by_sources(feed.sources)
        await self._feed_repo.set_news_items(feed.id, {item.url for item in items})


    async def remove_feed(self, feed_id: UUID) -> bool:
        return await self._feed_repo.delete(feed_id)


    async def get_feed(self, feed_id: UUID) -> Feed | None:
        return await self._feed_repo.get(feed_id)


    async def get_all_feeds(self) -> list[Feed]:
        return await self._feed_repo.get_all()


    async def get_all_sources(self) -> list[SourceConfig]:
        return await self._source_repo.get_all()


    async def add_source(self, config: SourceConfig) -> None:
        if config.type == "telegram" and self._tg is not None:
            await self._tg.join_channel(config.url)
        await self._source_repo.save(config)
        logger.info("Source saved: %s", config.url)


    async def remove_source(self, url: str) -> bool:
        return await self._source_repo.delete(url)


    async def mark_read(self, feed_id: UUID, news_url: str) -> None:
        await self._news_repo.mark_read(feed_id, news_url)


    async def mark_all_read(self, feed_id: UUID) -> None:
        await self._news_repo.mark_all_read(feed_id)


    async def mark_unread(self, feed_id: UUID, news_url: str) -> None:
        await self._news_repo.mark_unread(feed_id, news_url)


    async def get_stats(self, feed_id: UUID) -> FeedStats:
        return await self._news_repo.get_stats(feed_id)


    async def get_news(
        self,
        feed_id: UUID,
        *,
        unread_only: bool = False,
        all_time: bool = False,
        limit: int = 100,
        q: str | None = None
    ) -> list[NewsItem]:
        feed = await self._feed_repo.get(feed_id)
        keywords = feed.keywords if feed else None
        blacklist = feed.blacklist if feed else None
        not_before = (datetime.now(timezone.utc) - feed.max_age) if (feed and feed.max_age and not all_time) else None
        return await self._news_repo.get_by_feed(
            feed_id, keywords=keywords, blacklist=blacklist, not_before=not_before, unread_only=unread_only, limit=limit, q=q
        )


    async def fetch_all(self) -> None:
        feeds: list[Feed] = await self._feed_repo.get_all()
        sources: list[SourceConfig] = await self._source_repo.get_all()

        needed_urls: set[str] = {url for feed in feeds for url in feed.sources}
        parsers: list[Parser] = []
        for cfg in sources:
            if cfg.url not in needed_urls:
                continue
            try:
                parsers.append(self._factory.create(cfg))
            except ValueError:
                logger.warning("Skipping source '%s': no suitable parser available", cfg.url)

        if not parsers: return

        async for parser, items in aggregator.fetch(parsers):
            relevant_feeds: list[Feed] = [feed for feed in feeds if parser.url in feed.sources]
            for item in items:
                is_new: bool = await self._news_repo.save(item)
                if not is_new: continue

                for feed in relevant_feeds:
                    await self._news_repo.link_to_feed(feed.id, item.url)
