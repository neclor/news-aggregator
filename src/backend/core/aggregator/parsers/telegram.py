import logging

from telethon import TelegramClient

from backend.models import NewsItem
from backend.core.aggregator.parsers.parser import Parser


logger: logging.Logger = logging.getLogger(__name__)


class TelegramParser(Parser):
    def __init__(self, client: TelegramClient, channel: str, limit: int = 50) -> None:
        self._client = client
        self._channel = channel
        self._limit = limit


    @property
    def url(self) -> str:
        return self._channel


    async def fetch(self) -> list[NewsItem]:
        logger.debug("Fetching %d messages from %s", self._limit, self._channel)
        items = [
            self._to_news_item(m)
            async for m in self._client.iter_messages(self._channel, limit=self._limit)
            if m.message
        ]
        logger.info("Fetched %d items from %s", len(items), self._channel)
        return items


    def _to_news_item(self, message) -> NewsItem:
        text = message.message or ""
        return NewsItem(
            source=self._channel,
            url=f"https://t.me/{_channel_username(self._channel)}/{message.id}",
            title=text.split("\n", 1)[0][:200],
            text=text,
            published_at=message.date,
            author=None,
        )


def _channel_username(channel: str) -> str:
    if channel.startswith("@"):
        return channel[1:]
    return channel.rstrip("/").rsplit("/", 1)[-1]
