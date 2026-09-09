CREATE TABLE feed_reads (
    feed_id  TEXT NOT NULL REFERENCES feeds(id)      ON DELETE CASCADE,
    news_url TEXT NOT NULL REFERENCES news_items(url) ON DELETE CASCADE,
    PRIMARY KEY (feed_id, news_url)
);

INSERT INTO feed_reads (feed_id, news_url)
SELECT feed_id, news_url FROM feed_items WHERE is_read = 1;

DROP TABLE feed_items;

CREATE VIEW feed_items AS
SELECT fs.feed_id               AS feed_id,
       n.url                    AS news_url,
       n.source                 AS source,
       n.published_at           AS published_at,
       (r.news_url IS NOT NULL) AS is_read
FROM feed_sources fs
JOIN news_items n      ON n.source = fs.source_url
LEFT JOIN feed_reads r ON r.feed_id = fs.feed_id AND r.news_url = n.url;

CREATE INDEX idx_feed_reads_news ON feed_reads(news_url);

DROP INDEX IF EXISTS idx_news_items_source;
CREATE INDEX idx_news_items_source_pub ON news_items(source, published_at DESC);
