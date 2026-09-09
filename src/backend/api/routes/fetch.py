from fastapi import APIRouter

from backend.api.deps import FetchServiceDep


router = APIRouter(tags=["fetch"])


@router.post("/fetch", status_code=204)
async def trigger_fetch(service: FetchServiceDep) -> None:
    await service.fetch_all()
