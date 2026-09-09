# News Aggregator

[news.neclor.com](https://news.neclor.com)
[Telegram bot](https://t.me/neclor_news_aggregator_bot)

## About

Collects news from RSS feeds, websites, and Telegram channels into a single feed.
Includes a web UI, REST API, and Telegram bot for notifications.

## How it works

- The **backend** polls every registered source every `FETCH_INTERVAL_SEC` and
  stores items in SQLite.
- A **feed** is a named set of sources plus optional keyword / blacklist filters
  and a max age. Feed membership is derived automatically from the source list
  (the `feed_items` table is a view over `feed_sources` × `news_items`); only the
  per-feed read state is stored, in `feed_reads`.
- After each fetch cycle, items older than `RETENTION_DAYS` are pruned.
- The **web UI** (`src/site`) and **Telegram bot** (`src/bot`) both talk to the
  backend over the REST API.

## Running with Docker

```bash
cp .env.example .env
# fill in the Telegram credentials (see Configuration)
docker compose up -d
```

The web UI / API is served on `SERVER_PORT` (default `8080`). SQLite data lives in
the `news-aggregator-data` volume; Telegram session files in `HOST_SESSIONS_DIR`.

## Configuration

All settings are environment variables (see `.env.example`).

| Variable | Default | Purpose |
|---|---|---|
| `SERVER_PORT` | `8080` | Host port for the web UI / API |
| `HOST_SESSIONS_DIR` | `./sessions` | Host path for Telegram session files |
| `FETCH_INTERVAL_SEC` | `600` | Seconds between fetch cycles |
| `RETENTION_DAYS` | `30` | Delete news older than this after each cycle; `0` disables pruning |
| `TG_BACKEND_API_ID` / `TG_BACKEND_API_HASH` | — | Telegram API credentials for reading channels ([my.telegram.org](https://my.telegram.org)) |
| `TG_BACKEND_RECONNECT_DELAY` | `60` | Backend Telegram reconnect delay |
| `TG_BOT_API_ID` / `TG_BOT_API_HASH` / `TG_BOT_TOKEN` | — | Telegram bot credentials |
| `BOT_POLL_INTERVAL` | `600` | Seconds between bot notification checks |

Without `TG_BACKEND_*` the backend still runs, but Telegram sources are
unavailable.

## Local development

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m backend      # API on :8000, starts the fetch loop
PYTHONPATH=src python -m bot          # Telegram bot

cd src/site && npm ci && npm run dev  # web UI
```

The backend applies pending SQL migrations from `src/backend/db/migrations` on
startup.

## Releasing & deployment

CI/CD is driven by GitHub releases:

1. **Push / PR** — `Build backend docker`, `Build bot docker`, `Build Site` run
   as checks only (images are built but not pushed, nothing is deployed).
2. **Push a `X.Y.Z` tag** — `Release` builds and pushes the `backend` / `bot`
   images to `ghcr.io/<repo>/{backend,bot}` tagged `X.Y.Z` and `latest`, builds
   the site, and stages a **draft** GitHub release with `news-aggregator-site.zip`.
3. **Publish the draft release** — triggers the deploy workflows:
   - `Deploy backend, bot` — SSH to the server, `podman compose pull && up -d`
   - `Deploy UI (Server)` — download the release's site zip, unpack into `WEB_DIR`
   - `Deploy UI (GitHub Pages)` — publish the same zip to GitHub Pages

```bash
git tag 1.2.3
git push origin main 1.2.3
# then publish the draft release on GitHub
```

Required repository secrets: `SSH_HOST`, `SSH_USER`, `SSH_PORT`, `SSH_KEY`.
Required repository variables: `SERVER_DIR`, `WEB_DIR`, `VITE_API_BASE`.
