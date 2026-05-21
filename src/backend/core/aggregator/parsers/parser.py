from abc import ABC, abstractmethod

from backend.models import NewsItem


class Parser(ABC):
    @property
    @abstractmethod
    def url(self) -> str: ...

    @abstractmethod
    async def fetch(self) -> list[NewsItem]: ...
