import re
from datetime import datetime, timezone
from uuid import UUID

import aiosqlite

from backend.models.feed_stats import DayCount, FeedStats, SourceCount
from backend.models.news_item import NewsItem


class NewsRepository:
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db


    async def save(self, item: NewsItem) -> bool:
        fetched_at = datetime.now(timezone.utc).isoformat()
        async with self._db.execute(
            """
            INSERT OR IGNORE INTO news_items (url, source, title, text, published_at, fetched_at, author)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (item.url, item.source, item.title, item.text, item.published_at.isoformat(), fetched_at, item.author),
        ) as cursor:
            inserted = cursor.rowcount > 0
        if inserted:
            await self._db.execute(
                "INSERT INTO news_fts(url, title, text) VALUES (?, ?, ?)",
                (item.url, item.title, item.text),
            )
        await self._db.commit()
        return inserted


    async def link_to_feed(self, feed_id: UUID, news_url: str) -> None:
        await self._db.execute(
            "INSERT OR IGNORE INTO feed_items (feed_id, news_url) VALUES (?, ?)",
            (str(feed_id), news_url),
        )
        await self._db.commit()


    async def get_by_feed(self, feed_id: UUID, *, keywords: list[str] | None = None, not_before: datetime | None = None, unread_only: bool = False, limit: int = 100, q: str | None = None) -> list[NewsItem]:
        query = """
            SELECT news_items.*, feed_items.is_read FROM news_items
            JOIN feed_items ON feed_items.news_url = news_items.url
            WHERE feed_items.feed_id = ?
        """
        params: list = [str(feed_id)]
        if not_before is not None:
            query += " AND news_items.published_at >= ?"
            params.append(not_before.isoformat())
        if unread_only:
            query += " AND feed_items.is_read = 0"
        if q:
            fts_q = _fts_query(q)
            if fts_q:
                query += " AND news_items.url IN (SELECT url FROM news_fts WHERE news_fts MATCH ?)"
                params.append(fts_q)
        query += " ORDER BY news_items.published_at DESC"

        async with self._db.execute(query, params) as cursor:
            rows = await cursor.fetchall()

        items = [_row_to_item(r) for r in rows]
        if keywords:
            pattern = re.compile(r'\b(' + '|'.join(re.escape(kw.lower()) for kw in keywords) + r')\b')
            items = [i for i in items if pattern.search(f"{i.title} {i.text}".lower())]
        return items[:limit]


    async def get_by_sources(self, sources: list[str]) -> list[NewsItem]:
        if not sources:
            return []
        placeholders = ",".join("?" * len(sources))
        async with self._db.execute(
            f"SELECT * FROM news_items WHERE source IN ({placeholders})",
            sources,
        ) as cursor:
            rows = await cursor.fetchall()
        return [_row_to_item(r) for r in rows]


    async def mark_read(self, feed_id: UUID, news_url: str) -> None:
        await self._db.execute(
            "UPDATE feed_items SET is_read = 1 WHERE feed_id = ? AND news_url = ?",
            (str(feed_id), news_url),
        )
        await self._db.commit()


    async def mark_all_read(self, feed_id: UUID) -> None:
        await self._db.execute(
            "UPDATE feed_items SET is_read = 1 WHERE feed_id = ?",
            (str(feed_id),),
        )
        await self._db.commit()


    async def mark_unread(self, feed_id: UUID, news_url: str) -> None:
        await self._db.execute(
            "UPDATE feed_items SET is_read = 0 WHERE feed_id = ? AND news_url = ?",
            (str(feed_id), news_url),
        )
        await self._db.commit()


    async def get_stats(self, feed_id: UUID) -> FeedStats:
        fid = str(feed_id)

        async with self._db.execute(
            "SELECT COUNT(*) AS total, SUM(is_read) AS read_count FROM feed_items WHERE feed_id = ?",
            (fid,),
        ) as cur:
            row = await cur.fetchone()
        total: int = (row["total"] or 0) if row else 0
        read_count: int = (row["read_count"] or 0) if row else 0

        async with self._db.execute(
            """
            SELECT news_items.source, COUNT(*) AS cnt
            FROM feed_items
            JOIN news_items ON news_items.url = feed_items.news_url
            WHERE feed_items.feed_id = ?
            GROUP BY news_items.source
            ORDER BY cnt DESC
            LIMIT 10
            """,
            (fid,),
        ) as cur:
            by_source = [SourceCount(source=r["source"], count=r["cnt"]) for r in await cur.fetchall()]

        async with self._db.execute(
            """
            SELECT DATE(news_items.published_at) AS day, COUNT(*) AS cnt
            FROM feed_items
            JOIN news_items ON news_items.url = feed_items.news_url
            WHERE feed_items.feed_id = ?
              AND news_items.published_at >= DATE('now', '-6 days')
            GROUP BY day
            ORDER BY day
            """,
            (fid,),
        ) as cur:
            daily = [DayCount(date=r["day"], count=r["cnt"]) for r in await cur.fetchall()]

        return FeedStats(total=total, read=read_count, unread=total - read_count, by_source=by_source, daily=daily)


def _fts_query(q: str) -> str:
    tokens = [t.replace('"', '') for t in q.split() if t.replace('"', '')]
    return ' '.join(f'"{t}"' for t in tokens)


def _row_to_item(row: aiosqlite.Row) -> NewsItem:
    return NewsItem(
        url=row["url"],
        source=row["source"],
        title=row["title"],
        text=row["text"],
        published_at=datetime.fromisoformat(row["published_at"]),
        author=row["author"],
        is_read=bool(row["is_read"]) if "is_read" in row.keys() else False,
    )
