from datetime import datetime, timezone
from typing import Any

from telethon import TelegramClient
from telethon.events import NewMessage

from .api import ApiClient
from .store import Store


HELP = (
    "**News Aggregator Bot**\n\n"
    "/feeds — list available feeds\n"
    "/subscribe N — subscribe to feed number N\n"
    "/unsubscribe — cancel subscription\n"
    "/status — current subscription"
)


class Handlers:
    def __init__(self, store: Store, api: ApiClient) -> None:
        self._store = store
        self._api = api


    def register(self, bot: TelegramClient) -> None:
        bot.add_event_handler(self._on_start,       NewMessage(pattern=r"^/start$|^/help$"))
        bot.add_event_handler(self._on_feeds,       NewMessage(pattern=r"^/feeds$"))
        bot.add_event_handler(self._on_subscribe,   NewMessage(pattern=r"^/subscribe"))
        bot.add_event_handler(self._on_unsubscribe, NewMessage(pattern=r"^/unsubscribe$"))
        bot.add_event_handler(self._on_status,      NewMessage(pattern=r"^/status$"))


    async def _on_start(self, event: Any) -> None:
        await event.reply(HELP)


    async def _on_feeds(self, event: Any) -> None:
        try:
            feeds = await self._api.get_feeds()
        except Exception:
            await event.reply("Could not reach the server. Is the backend running?")
            return

        if not feeds:
            await event.reply("No feeds configured yet. Set them up in the web panel.")
            return

        lines = "\n".join(f"{i + 1}. {f.name}" for i, f in enumerate(feeds))
        await event.reply(f"**Available feeds:**\n{lines}\n\nUse `/subscribe N` to subscribe.")


    async def _on_subscribe(self, event: Any) -> None:
        text: str = event.text or ""
        parts = text.split(maxsplit=1)
        arg = parts[1].strip() if len(parts) > 1 else ""

        try:
            feeds = await self._api.get_feeds()
        except Exception:
            await event.reply("Could not reach the server.")
            return

        try:
            n = int(arg) - 1
            if n < 0:
                raise ValueError
            feed = feeds[n]
        except ValueError:
            await event.reply("Provide a feed number. Example: `/subscribe 1`\n\nUse /feeds to see the list.")
            return
        except IndexError:
            await event.reply(f"No feed #{arg}. Use /feeds to see the list.")
            return

        self._store.save(int(event.chat_id), feed.id, datetime.now(timezone.utc))
        await event.reply(f"Subscribed to **{feed.name}**.\nYou'll receive new articles as they arrive.")


    async def _on_unsubscribe(self, event: Any) -> None:
        if self._store.get(int(event.chat_id)) is None:
            await event.reply("You don't have an active subscription.")
            return
        self._store.remove(int(event.chat_id))
        await event.reply("Unsubscribed.")


    async def _on_status(self, event: Any) -> None:
        sub = self._store.get(int(event.chat_id))
        if sub is None:
            await event.reply("No active subscription. Use /feeds to browse.")
            return

        try:
            feeds = await self._api.get_feeds()
            feed = next((f for f in feeds if f.id == sub.feed_id), None)
            name = feed.name if feed else sub.feed_id
        except Exception:
            name = sub.feed_id

        await event.reply(f"Subscribed to: **{name}**")
