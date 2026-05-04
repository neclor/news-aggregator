# News Aggregator

Aggregates news from RSS feeds, websites, and Telegram channels. Includes a web UI, REST API, and Telegram bot.

## Components

- **Backend** — FastAPI, fetches news and serves it via REST API
- **Frontend** — web interface for reading news
- **Bot** — Telegram bot for notifications

## Running

### Requirements

- Docker and Docker Compose

### Configuration

Copy `.env.example` and fill in the values:

```bash
cp configs/.env.example configs/.env
```

```env
TG_API_ID=       # api_id from my.telegram.org
TG_API_HASH=     # api_hash from my.telegram.org
TG_BOT_TOKEN=    # bot token from @BotFather
```

`TG_API_ID` and `TG_API_HASH` are only needed if you use Telegram channels as sources.

### Start

```bash
docker-compose up -d
```

Web UI will be available at `http://localhost:5300`.

## Sources

Supported source types:

- **RSS** — any RSS/Atom feed
- **Telegram** — channels (by `@username` or `t.me/...` link)
- **Site** — website scraping via CSS selectors

## Data

The database and session files are stored in the `data/` folder. News is fetched automatically every 10 minutes.
