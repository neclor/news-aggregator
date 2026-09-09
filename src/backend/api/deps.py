from typing import Annotated

from fastapi import Depends, Request

from backend.services.news_service import NewsService


def get_service(request: Request) -> NewsService:
    return request.app.state.service


def get_fetch_service(request: Request) -> NewsService:
    return request.app.state.fetch_service


NewsServiceDep = Annotated[NewsService, Depends(get_service)]
FetchServiceDep = Annotated[NewsService, Depends(get_fetch_service)]
