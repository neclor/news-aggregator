CREATE TRIGGER IF NOT EXISTS news_items_ai AFTER INSERT ON news_items
BEGIN
    INSERT INTO news_fts(url, title, text) VALUES (new.url, new.title, new.text);
END;

CREATE TRIGGER IF NOT EXISTS news_items_ad AFTER DELETE ON news_items
BEGIN
    INSERT INTO news_fts(news_fts, url, title, text)
    VALUES('delete', old.url, old.title, old.text);
END;

CREATE TRIGGER IF NOT EXISTS news_items_au AFTER UPDATE ON news_items
BEGIN
    INSERT INTO news_fts(news_fts, url, title, text)
    VALUES('delete', old.url, old.title, old.text);
    INSERT INTO news_fts(url, title, text)
    VALUES (new.url, new.title, new.text);
END;
