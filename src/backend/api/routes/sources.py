from urllib.parse import unquote

from fastapi import APIRouter, HTTPException

from backend.api.deps import NewsServiceDep
from backend.api.schemas import SourceIn, SourceOut
from backend.models.site_selectors import SiteSelectors
from backend.models.source_config import SourceConfig
from backend.utils.url_utils import normalize_url


router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceOut])
async def get_sources(service: NewsServiceDep) -> list[SourceOut]:
    return [SourceOut(url=s.url, type=s.type) for s in await service.get_all_sources()]


@router.post("", response_model=SourceOut, status_code=201)
async def create_source(body: SourceIn, service: NewsServiceDep) -> SourceOut:
    selectors = (
        SiteSelectors(
            articles=body.selectors.articles,
            title=body.selectors.title,
            url=body.selectors.url,
            text=body.selectors.text,
        )
        if body.selectors
        else None
    )
    config = SourceConfig(url=body.url, type=body.type, selectors=selectors)
    try:
        await service.add_source(config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return SourceOut(url=config.url, type=config.type)


@router.delete("/{source_url:path}", status_code=204)
async def delete_source(source_url: str, service: NewsServiceDep) -> None:
    if not await service.remove_source(normalize_url(unquote(source_url))):
        raise HTTPException(status_code=404)
