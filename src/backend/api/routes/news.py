from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from backend.api.deps import NewsServiceDep
from backend.api.schemas import FeedStatsOut, MarkReadIn, NewsItemOut
from backend.models.news_item import NewsItem
from backend.utils.url_utils import normalize_url


router = APIRouter(prefix="/feeds/{feed_id}/news", tags=["news"])


@router.get("", response_model=list[NewsItemOut])
async def get_news(
    feed_id: UUID,
    service: NewsServiceDep,
    unread_only: bool = False,
    all_time: bool = False,
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[NewsItemOut]:
    if not await service.get_feed(feed_id):
        raise HTTPException(status_code=404)
    items = await service.get_news(feed_id, unread_only=unread_only, all_time=all_time, limit=limit)
    return [_to_out(i) for i in items]


@router.get("/stats", response_model=FeedStatsOut)
async def get_stats(feed_id: UUID, service: NewsServiceDep) -> FeedStatsOut:
    if not await service.get_feed(feed_id):
        raise HTTPException(status_code=404)
    stats = await service.get_stats(feed_id)
    return FeedStatsOut(
        total=stats.total,
        read=stats.read,
        unread=stats.unread,
        by_source=[{"source": s["source"], "count": s["count"]} for s in stats.by_source],
        daily=[{"date": d["date"], "count": d["count"]} for d in stats.daily],
    )


@router.post("/read", status_code=204)
async def mark_all_read(feed_id: UUID, service: NewsServiceDep) -> None:
    if not await service.get_feed(feed_id):
        raise HTTPException(status_code=404)
    await service.mark_all_read(feed_id)


@router.post("/mark-read", status_code=204)
async def mark_read(feed_id: UUID, body: MarkReadIn, service: NewsServiceDep) -> None:
    if not await service.get_feed(feed_id):
        raise HTTPException(status_code=404)
    await service.mark_read(feed_id, normalize_url(body.url))


@router.post("/mark-unread", status_code=204)
async def mark_unread(feed_id: UUID, body: MarkReadIn, service: NewsServiceDep) -> None:
    if not await service.get_feed(feed_id):
        raise HTTPException(status_code=404)
    await service.mark_unread(feed_id, normalize_url(body.url))


def _to_out(item: NewsItem) -> NewsItemOut:
    return NewsItemOut(
        url=item.url,
        source=item.source,
        title=item.title,
        text=item.text,
        published_at=item.published_at,
        author=item.author,
        is_read=item.is_read,
    )
