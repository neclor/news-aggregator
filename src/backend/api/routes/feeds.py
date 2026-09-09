from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.api.deps import NewsServiceDep
from backend.api.schemas import FeedIn, FeedOut
from backend.models import Feed


router = APIRouter(prefix="/feeds", tags=["feeds"])


@router.get("", response_model=list[FeedOut])
async def get_feeds(service: NewsServiceDep) -> list[FeedOut]:
    return [_to_out(f) for f in await service.get_all_feeds()]


@router.post("", response_model=FeedOut, status_code=201)
async def create_feed(body: FeedIn, service: NewsServiceDep) -> FeedOut:
    feed = Feed(
        name=body.name,
        sources=body.sources,
        keywords=body.keywords,
        blacklist=body.blacklist,
        max_age=timedelta(hours=body.max_age_hours) if body.max_age_hours else None,
    )
    await service.add_feed(feed)
    return _to_out(feed)


@router.get("/{feed_id}", response_model=FeedOut)
async def get_feed(feed_id: UUID, service: NewsServiceDep) -> FeedOut:
    feed = await service.get_feed(feed_id)
    if not feed:
        raise HTTPException(status_code=404)
    return _to_out(feed)


@router.put("/{feed_id}", response_model=FeedOut)
async def update_feed(feed_id: UUID, body: FeedIn, service: NewsServiceDep) -> FeedOut:
    feed = Feed(
        id=feed_id,
        name=body.name,
        sources=body.sources,
        keywords=body.keywords,
        blacklist=body.blacklist,
        max_age=timedelta(hours=body.max_age_hours) if body.max_age_hours else None,
    )
    await service.update_feed(feed)
    return _to_out(feed)


@router.delete("/{feed_id}", status_code=204)
async def delete_feed(feed_id: UUID, service: NewsServiceDep) -> None:
    if not await service.remove_feed(feed_id):
        raise HTTPException(status_code=404)


def _to_out(feed: Feed) -> FeedOut:
    return FeedOut(
        id=feed.id,
        name=feed.name,
        sources=feed.sources,
        keywords=feed.keywords,
        blacklist=feed.blacklist,
        max_age_hours=feed.max_age.total_seconds() / 3600 if feed.max_age else None,
    )
