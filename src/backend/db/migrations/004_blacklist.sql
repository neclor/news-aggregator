CREATE TABLE feed_blacklist (
    feed_id TEXT NOT NULL REFERENCES feeds(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    PRIMARY KEY (feed_id, keyword)
);
