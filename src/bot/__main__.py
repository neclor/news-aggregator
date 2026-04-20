import asyncio
import logging

import httpx
from telethon import TelegramClient

from .configs import bot_config
from .api import ApiClient
from .handlers import Handlers
from .notifier import Notifier
from .store import Store


logger = logging.getLogger(__name__)


async def main() -> None:
    if not bot_config.BOT_TOKEN:
        raise RuntimeError("TG_BOT_TOKEN is not set in configs/.env")

    store = Store(bot_config.DATA_FILE)

    async with httpx.AsyncClient() as http:
        api = ApiClient(bot_config.API_BASE, http)
        bot = _build_client()

        Handlers(store, api).register(bot)
        notifier = Notifier(bot, api, store, bot_config.POLL_INTERVAL)

        await bot.start(bot_token=bot_config.BOT_TOKEN)  # type: ignore[misc]
        logger.info("Bot started. Poll interval: %ds", bot_config.POLL_INTERVAL)

        asyncio.create_task(notifier.run())

        await bot.run_until_disconnected()  # type: ignore[misc]


def _build_client() -> TelegramClient:
    return TelegramClient(
        str(bot_config.SESSION_PATH),
        bot_config.API_ID,
        bot_config.API_HASH,
        connection_retries=-1,
        retry_delay=10,
    )


if __name__ == "__main__": asyncio.run(main())
