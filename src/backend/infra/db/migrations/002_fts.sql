CREATE VIRTUAL TABLE news_fts USING fts5(
    url   UNINDEXED,
    title,
    text
);

INSERT INTO news_fts(url, title, text)
SELECT url, title, text FROM news_items;
