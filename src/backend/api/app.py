from fastapi import FastAPI

from backend.api.routes import feeds, fetch, news, sources


app = FastAPI(title="News Aggregator")
app.include_router(feeds.router)
app.include_router(news.router)
app.include_router(sources.router)
app.include_router(fetch.router)
