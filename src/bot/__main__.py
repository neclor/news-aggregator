import asyncio
import logging

import httpx
from telethon import TelegramClient

from .configs import bot_config
from .api import ApiClient
from .services import Handlers, Notifier
from .storage import Store


logger = logging.getLogger(__name__)


async def main() -> None:
    if not bot_config.TG_BOT_TOKEN:
        raise RuntimeError("TG_BOT_TOKEN is not set")

    store = Store(bot_config.BOT_DATA_PATH)

    async with httpx.AsyncClient() as http:
        api = ApiClient(bot_config.BACKEND_URL, http)
        bot = _build_client()

        Handlers(store, api).register(bot)
        notifier = Notifier(bot, api, store, bot_config.BOT_POLL_INTERVAL)

        await bot.start(bot_token=bot_config.TG_BOT_TOKEN)  # type: ignore[misc]
        logger.info("Bot started. Poll interval: %ds", bot_config.BOT_POLL_INTERVAL)

        notify_task = asyncio.create_task(notifier.run(), name="notifier")

        await bot.run_until_disconnected()  # type: ignore[misc]
        notify_task.cancel()
        await asyncio.gather(notify_task, return_exceptions=True)


def _build_client() -> TelegramClient:
    return TelegramClient(
        bot_config.TG_BOT_SESSION_PATH,
        bot_config.TG_BOT_API_ID,
        bot_config.TG_BOT_API_HASH,
        connection_retries=-1,
        retry_delay=10,
    )


if __name__ == "__main__": asyncio.run(main())
