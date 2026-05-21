import json

import aiosqlite

from backend.models import DEFAULT_LIMIT, SourceConfig, SiteSelectors


class SourceRepository:
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db


    async def save(self, config: SourceConfig) -> None:
        extra: dict = {}
        if config.selectors:
            extra["selectors"] = {
                "articles": config.selectors.articles,
                "title": config.selectors.title,
                "url": config.selectors.url,
                "text": config.selectors.text,
            }
        if config.limit != DEFAULT_LIMIT:
            extra["limit"] = config.limit

        await self._db.execute(
            """
            INSERT INTO sources (url, type, config)
            VALUES (?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                type   = excluded.type,
                config = excluded.config
            """,
            (config.url, config.type, json.dumps(extra)),
        )
        await self._db.commit()


    async def delete(self, url: str) -> bool:
        async with self._db.execute(
            "DELETE FROM sources WHERE url = ?", (url,)
        ) as cursor:
            deleted = cursor.rowcount > 0
        await self._db.commit()
        return deleted


    async def exists(self, url: str) -> bool:
        async with self._db.execute(
            "SELECT EXISTS(SELECT 1 FROM sources WHERE url = ?)", (url,)
        ) as cursor:
            row = await cursor.fetchone()
        return bool(row[0]) if row else False


    async def get_all(self) -> list[SourceConfig]:
        async with self._db.execute("SELECT * FROM sources") as cursor:
            rows = await cursor.fetchall()
        return [_row_to_config(r) for r in rows]


def _row_to_config(row: aiosqlite.Row) -> SourceConfig:
    extra: dict = json.loads(row["config"])
    selectors: SiteSelectors | None = None
    if "selectors" in extra:
        s: dict = extra["selectors"]
        selectors = SiteSelectors(
            articles=s["articles"],
            title=s["title"],
            url=s["url"],
            text=s.get("text", ""),
        )
    return SourceConfig(
        url=row["url"],
        type=row["type"],
        selectors=selectors,
        limit=extra.get("limit", DEFAULT_LIMIT),
    )
