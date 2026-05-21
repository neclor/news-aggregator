from datetime import timedelta
from uuid import UUID

import aiosqlite

from backend.models import Feed


class FeedRepository:
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db


    async def save(self, feed: Feed) -> None:
        await self._db.execute(
            """
            INSERT INTO feeds (id, name, max_age_sec)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name        = excluded.name,
                max_age_sec = excluded.max_age_sec
            """,
            (str(feed.id), feed.name,
             feed.max_age.total_seconds() if feed.max_age else None),
        )
        await self._db.execute(
            "DELETE FROM feed_sources WHERE feed_id = ?", (str(feed.id),)
        )
        await self._db.executemany(
            "INSERT INTO feed_sources (feed_id, source_url) VALUES (?, ?)",
            [(str(feed.id), url) for url in feed.sources],
        )
        await self._db.execute(
            "DELETE FROM feed_keywords WHERE feed_id = ?", (str(feed.id),)
        )
        await self._db.executemany(
            "INSERT INTO feed_keywords (feed_id, keyword) VALUES (?, ?)",
            [(str(feed.id), kw) for kw in feed.keywords],
        )
        await self._db.execute(
            "DELETE FROM feed_blacklist WHERE feed_id = ?", (str(feed.id),)
        )
        await self._db.executemany(
            "INSERT INTO feed_blacklist (feed_id, keyword) VALUES (?, ?)",
            [(str(feed.id), kw) for kw in feed.blacklist],
        )
        await self._db.commit()


    async def set_news_items(self, feed_id: UUID, news_urls: set[str]) -> None:
        fid = str(feed_id)
        if not news_urls:
            await self._db.execute("DELETE FROM feed_items WHERE feed_id = ?", (fid,))
            await self._db.commit()
            return
        placeholders = ",".join("?" * len(news_urls))
        await self._db.execute(
            f"DELETE FROM feed_items WHERE feed_id = ? AND news_url NOT IN ({placeholders})",
            [fid, *news_urls],
        )
        await self._db.executemany(
            "INSERT OR IGNORE INTO feed_items (feed_id, news_url) VALUES (?, ?)",
            [(fid, url) for url in news_urls],
        )
        await self._db.commit()

    async def delete(self, feed_id: UUID) -> bool:
        async with self._db.execute(
            "DELETE FROM feeds WHERE id = ?", (str(feed_id),)
        ) as cursor:
            deleted = cursor.rowcount > 0
        await self._db.commit()
        return deleted


    async def get(self, feed_id: UUID) -> Feed | None:
        async with self._db.execute(
            "SELECT * FROM feeds WHERE id = ?", (str(feed_id),)
        ) as cursor:
            row = await cursor.fetchone()
        if not row:
            return None
        return await self._load_feed(row)


    async def get_all(self) -> list[Feed]:
        async with self._db.execute("SELECT * FROM feeds") as cursor:
            feed_rows = await cursor.fetchall()
        if not feed_rows:
            return []

        ids = [r["id"] for r in feed_rows]
        ph = ",".join("?" * len(ids))

        async with self._db.execute(
            f"SELECT feed_id, source_url FROM feed_sources WHERE feed_id IN ({ph})", ids
        ) as cursor:
            src_rows = await cursor.fetchall()

        async with self._db.execute(
            f"SELECT feed_id, keyword FROM feed_keywords WHERE feed_id IN ({ph})", ids
        ) as cursor:
            kw_rows = await cursor.fetchall()

        async with self._db.execute(
            f"SELECT feed_id, keyword FROM feed_blacklist WHERE feed_id IN ({ph})", ids
        ) as cursor:
            bl_rows = await cursor.fetchall()

        sources: dict[str, list[str]] = {}
        for r in src_rows:
            sources.setdefault(r["feed_id"], []).append(r["source_url"])

        keywords: dict[str, list[str]] = {}
        for r in kw_rows:
            keywords.setdefault(r["feed_id"], []).append(r["keyword"])

        blacklist: dict[str, list[str]] = {}
        for r in bl_rows:
            blacklist.setdefault(r["feed_id"], []).append(r["keyword"])

        return [
            Feed(
                id=UUID(r["id"]),
                name=r["name"],
                sources=sources.get(r["id"], []),
                keywords=keywords.get(r["id"], []),
                blacklist=blacklist.get(r["id"], []),
                max_age=timedelta(seconds=r["max_age_sec"]) if r["max_age_sec"] is not None else None,
            )
            for r in feed_rows
        ]


    async def _load_feed(self, row: aiosqlite.Row) -> Feed:
        feed_id: str = row["id"]

        async with self._db.execute(
            "SELECT source_url FROM feed_sources WHERE feed_id = ?", (feed_id,)
        ) as cursor:
            sources = [r["source_url"] for r in await cursor.fetchall()]

        async with self._db.execute(
            "SELECT keyword FROM feed_keywords WHERE feed_id = ?", (feed_id,)
        ) as cursor:
            keywords = [r["keyword"] for r in await cursor.fetchall()]

        async with self._db.execute(
            "SELECT keyword FROM feed_blacklist WHERE feed_id = ?", (feed_id,)
        ) as cursor:
            blacklist = [r["keyword"] for r in await cursor.fetchall()]

        return Feed(
            name=row["name"],
            id=UUID(feed_id),
            sources=sources,
            keywords=keywords,
            blacklist=blacklist,
            max_age=(
                timedelta(seconds=row["max_age_sec"])
                if row["max_age_sec"] is not None
                else None
            )
        )
