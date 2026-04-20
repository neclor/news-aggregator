import asyncio
import logging
from datetime import datetime

from telethon import TelegramClient

from .api import ApiClient, NewsItem
from .store import Store


logger = logging.getLogger(__name__)


def _format(item: NewsItem) -> str:
    title = item.title or item.url
    excerpt = item.text[:300] + "…" if len(item.text) > 300 else item.text
    parts: list[str] = [f"**{item.source}**", f"[{title}]({item.url})"]
    if excerpt:
        parts.append(excerpt)
    return "\n".join(parts)


class Notifier:
    def __init__(
        self,
        bot: TelegramClient,
        api: ApiClient,
        store: Store,
        interval: int,
    ) -> None:
        self._bot = bot
        self._api = api
        self._store = store
        self._interval = interval


    async def run(self) -> None:
        while True:
            await asyncio.sleep(self._interval)
            await self._deliver_all()


    async def _deliver_all(self) -> None:
        for chat_id, sub in self._store.all():
            await self._deliver_to(chat_id, sub.feed_id, sub.last_seen)


    async def _deliver_to(self, chat_id: int, feed_id: str, last_seen: datetime) -> None:
        try:
            items = await self._api.get_news(feed_id)
        except Exception:
            logger.exception("Failed to fetch news for chat %d", chat_id)
            return

        new_items = sorted(
            (i for i in items if i.published_at > last_seen),
            key=lambda i: i.published_at,
        )

        for item in new_items:
            try:
                await self._bot.send_message(chat_id, _format(item), link_preview=False)
                self._store.update_last_seen(chat_id, item.published_at)
            except Exception:
                logger.exception("Failed to send to chat %d, will retry next cycle", chat_id)
                return
