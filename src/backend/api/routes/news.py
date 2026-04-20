from urllib.parse import unquote
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from backend.api.deps import NewsServiceDep
from backend.api.schemas import NewsItemOut
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


@router.post("/read", status_code=204)
async def mark_all_read(feed_id: UUID, service: NewsServiceDep) -> None:
    if not await service.get_feed(feed_id):
        raise HTTPException(status_code=404)
    await service.mark_all_read(feed_id)


@router.post("/{news_url:path}/read", status_code=204)
async def mark_read(feed_id: UUID, news_url: str, service: NewsServiceDep) -> None:
    if not await service.get_feed(feed_id):
        raise HTTPException(status_code=404)
    await service.mark_read(feed_id, normalize_url(unquote(news_url)))


def _to_out(item: NewsItem) -> NewsItemOut:
    return NewsItemOut(
        url=item.url,
        source=item.source,
        title=item.title,
        text=item.text,
        published_at=item.published_at,
        author=item.author,
    )
