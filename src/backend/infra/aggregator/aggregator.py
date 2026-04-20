import asyncio
import logging
from collections.abc import AsyncGenerator, Iterable

from backend.models.news_item import NewsItem
from backend.infra.aggregator.parsers.parser import Parser


logger: logging.Logger = logging.getLogger(__name__)


async def fetch(parsers: Iterable[Parser]) -> AsyncGenerator[tuple[Parser, list[NewsItem]], None]:
    tasks: dict[asyncio.Task, Parser] = {
        asyncio.create_task(parser.fetch(), name=parser.url): parser
        for parser in parsers
    }
    pending: set[asyncio.Task] = set(tasks)

    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            parser = tasks[task]
            if exc := task.exception():
                logger.error("Source '%s' failed: %s", parser.url, exc)
                continue
            yield parser, task.result()
