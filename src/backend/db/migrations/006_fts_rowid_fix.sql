-- news_fts is a regular (self-content) FTS5 table, but the 003 delete/update
-- triggers remove rows with the external-content 'delete' command, which errors
-- ("SQL logic error") on current SQLite and breaks every DELETE / UPDATE on
-- news_items -- retention pruning included.
--
-- Fix: align news_fts rowids with news_items.rowid, then rebuild the triggers to
-- maintain the index with plain DELETE ... WHERE rowid = ? / INSERT.

DROP TRIGGER news_items_ai;
DROP TRIGGER news_items_ad;
DROP TRIGGER news_items_au;

DELETE FROM news_fts;
INSERT INTO news_fts(rowid, url, title, text)
SELECT rowid, url, title, text FROM news_items;

CREATE TRIGGER news_items_ai AFTER INSERT ON news_items
BEGIN
    INSERT INTO news_fts(rowid, url, title, text)
    VALUES (new.rowid, new.url, new.title, new.text);
END;

CREATE TRIGGER news_items_ad AFTER DELETE ON news_items
BEGIN
    DELETE FROM news_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER news_items_au AFTER UPDATE ON news_items
BEGIN
    DELETE FROM news_fts WHERE rowid = old.rowid;
    INSERT INTO news_fts(rowid, url, title, text)
    VALUES (new.rowid, new.url, new.title, new.text);
END;
