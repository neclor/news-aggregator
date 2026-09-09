from datetime import datetime, timezone
from uuid import UUID

import aiosqlite

from backend.models import DayCount, FeedStats, SourceCount, NewsItem


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
        await self._db.commit()
        return inserted


    async def get_by_feed(
            self,
            feed_id: UUID,
            *,
            keywords: list[str] | None = None,
            blacklist: list[str] | None = None,
            not_before: datetime | None = None,
            unread_only: bool = False,
            limit: int = 100,
            q: str | None = None
    ) -> list[NewsItem]:
        query = """
            SELECT news_items.*, feed_items.is_read FROM feed_items
            JOIN news_items ON news_items.url = feed_items.news_url
            WHERE feed_items.feed_id = ?
        """
        params: list = [str(feed_id)]
        if not_before is not None:
            query += " AND feed_items.published_at >= ?"
            params.append(not_before.isoformat())
        if unread_only:
            query += " AND feed_items.is_read = 0"
        if keywords:
            fts_kw = _fts_query(keywords)
            if fts_kw:
                query += " AND news_items.url IN (SELECT url FROM news_fts WHERE news_fts MATCH ?)"
                params.append(fts_kw)
        if blacklist:
            fts_bl = _fts_query(blacklist)
            if fts_bl:
                query += " AND news_items.url NOT IN (SELECT url FROM news_fts WHERE news_fts MATCH ?)"
                params.append(fts_bl)
        if q:
            fts_q = _fts_query(q.split())
            if fts_q:
                query += " AND news_items.url IN (SELECT url FROM news_fts WHERE news_fts MATCH ?)"
                params.append(fts_q)
        query += " ORDER BY feed_items.published_at DESC LIMIT ?"
        params.append(limit)

        async with self._db.execute(query, params) as cursor:
            rows = await cursor.fetchall()

        return [_row_to_item(r) for r in rows]


    async def delete_older_than(self, cutoff: datetime, *, batch_size: int = 5000) -> int:
        cutoff_iso = cutoff.isoformat()
        total = 0
        while True:
            async with self._db.execute(
                """
                DELETE FROM news_items
                WHERE url IN (
                    SELECT url FROM news_items
                    WHERE published_at < ?
                    ORDER BY published_at
                    LIMIT ?
                )
                """,
                (cutoff_iso, batch_size),
            ) as cursor:
                deleted = cursor.rowcount
            await self._db.commit()
            total += deleted
            if deleted < batch_size:
                break
        return total


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
            "INSERT OR IGNORE INTO feed_reads (feed_id, news_url) VALUES (?, ?)",
            (str(feed_id), news_url),
        )
        await self._db.commit()


    async def mark_all_read(self, feed_id: UUID) -> None:
        await self._db.execute(
            """
            INSERT OR IGNORE INTO feed_reads (feed_id, news_url)
            SELECT feed_id, news_url FROM feed_items WHERE feed_id = ?
            """,
            (str(feed_id),),
        )
        await self._db.commit()


    async def mark_unread(self, feed_id: UUID, news_url: str) -> None:
        await self._db.execute(
            "DELETE FROM feed_reads WHERE feed_id = ? AND news_url = ?",
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
            SELECT source, COUNT(*) AS cnt
            FROM feed_items
            WHERE feed_id = ?
            GROUP BY source
            ORDER BY cnt DESC
            LIMIT 10
            """,
            (fid,),
        ) as cur:
            by_source = [SourceCount(source=r["source"], count=r["cnt"]) for r in await cur.fetchall()]

        async with self._db.execute(
            """
            SELECT DATE(published_at) AS day, COUNT(*) AS cnt
            FROM feed_items
            WHERE feed_id = ?
              AND published_at >= DATE('now', '-6 days')
            GROUP BY day
            ORDER BY day
            """,
            (fid,),
        ) as cur:
            daily = [DayCount(date=r["day"], count=r["cnt"]) for r in await cur.fetchall()]

        return FeedStats(total=total, read=read_count, unread=total - read_count, by_source=by_source, daily=daily)


def _fts_query(words: list[str]) -> str:
    tokens = [t.replace('"', '') for t in words if t.replace('"', '')]
    return ' OR '.join(f'"{t}"' for t in tokens)


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
