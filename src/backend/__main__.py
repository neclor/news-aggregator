import asyncio
import logging

import aiosqlite
import httpx
import uvicorn

from backend.api.app import app
from backend.configs import log_config, app_config
from backend.services.telegram_connection import TelegramConnection
from backend.infra.db.database import create_database
from backend.infra.db.feed_repo import FeedRepository
from backend.infra.db.news_repo import NewsRepository
from backend.infra.db.source_repo import SourceRepository
from backend.infra.aggregator.parser_factory import ParserFactory
from backend.services.news_service import NewsService


logger = logging.getLogger(__name__)


async def main() -> None:
    init()

    db: aiosqlite.Connection = await create_database(app_config.DB_PATH)
    tg: TelegramConnection | None = _setup_telegram()
    http: httpx.AsyncClient = httpx.AsyncClient()
    try:
        service: NewsService = _build_service(http, db, tg)
        app.state.service = service
        server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=8000))

        await asyncio.gather(run(service), server.serve())

    finally:
        await http.aclose()
        if tg: await tg.stop()
        await db.close()


def init() -> None:
    log_config.setup()


def _setup_telegram() -> TelegramConnection | None:
    if not (app_config.TG_API_ID and app_config.TG_API_HASH):
        logger.warning("Telegram credentials not set, TG sources will be unavailable")
        return None

    tg = TelegramConnection(str(app_config.TG_SESSION_PATH), app_config.TG_API_ID, app_config.TG_API_HASH)
    tg.start()
    return tg


def _build_service(http: httpx.AsyncClient, db: aiosqlite.Connection, tg: TelegramConnection | None) -> NewsService:
    factory = ParserFactory(http, tg.client if tg else None)
    return NewsService(
        factory=factory,
        news_repo=NewsRepository(db),
        feed_repo=FeedRepository(db),
        source_repo=SourceRepository(db),
        tg=tg,
    )


async def run(service: NewsService) -> None:
    while True:
        logger.info("Starting fetch cycle")

        try:
            await service.fetch_all()
        except Exception:
            logger.exception("Fetch cycle failed, retrying in %ds", app_config.FETCH_INTERVAL_SEC)
        else:
            logger.info("Fetch cycle done, sleeping %ds", app_config.FETCH_INTERVAL_SEC)

        await asyncio.sleep(app_config.FETCH_INTERVAL_SEC)


if __name__ == "__main__": asyncio.run(main())
