CREATE TABLE sources (
    url    TEXT PRIMARY KEY,
    type   TEXT NOT NULL CHECK(type IN ('rss', 'telegram', 'site')),
    config TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE feeds (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    max_age_sec REAL  -- NULL = no limit, stored as fractional seconds
);

CREATE TABLE feed_sources (
    feed_id     TEXT NOT NULL REFERENCES feeds(id)    ON DELETE CASCADE,
    source_url  TEXT NOT NULL REFERENCES sources(url) ON DELETE CASCADE,
    PRIMARY KEY (feed_id, source_url)
);

CREATE TABLE feed_keywords (
    feed_id TEXT NOT NULL REFERENCES feeds(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    PRIMARY KEY (feed_id, keyword)
);

CREATE TABLE news_items (
    url          TEXT PRIMARY KEY,
    source       TEXT NOT NULL,
    title        TEXT NOT NULL,
    text         TEXT NOT NULL,
    published_at TEXT NOT NULL,  -- ISO 8601 UTC
    fetched_at   TEXT NOT NULL,  -- ISO 8601 UTC
    author       TEXT
);

CREATE TABLE feed_items (
    feed_id  TEXT NOT NULL REFERENCES feeds(id)       ON DELETE CASCADE,
    news_url TEXT NOT NULL REFERENCES news_items(url) ON DELETE CASCADE,
    is_read  INTEGER NOT NULL DEFAULT 0 CHECK(is_read IN (0, 1)),
    PRIMARY KEY (feed_id, news_url)
);

CREATE INDEX idx_news_items_source      ON news_items(source);
CREATE INDEX idx_news_items_published   ON news_items(published_at DESC);
CREATE INDEX idx_feed_items_unread      ON feed_items(feed_id, is_read) WHERE is_read = 0;
CREATE INDEX idx_feed_sources_source    ON feed_sources(source_url);
