import logging
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite


logger = logging.getLogger(__name__)


_MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def create_database(path: Path) -> aiosqlite.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db: aiosqlite.Connection = await aiosqlite.connect(path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    await _migrate(db)
    return db


async def _migrate(db: aiosqlite.Connection) -> None:
    await db.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version    INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
    """)
    await db.commit()

    async with db.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version") as cur:
        row = await cur.fetchone()
        current: int = row[0] if row else 0

    migrations: list = sorted(
        (p for p in _MIGRATIONS_DIR.glob("*.sql") if _version(p) > current),
        key=_version,
    )

    for path in migrations:
        version = _version(path)
        logger.info("Applying migration %03d: %s", version, path.name)
        sql = path.read_text(encoding="utf-8")
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                await db.execute(statement)
        await db.execute(
            "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
            (version, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()
        logger.info("Migration %03d applied", version)


def _version(path: Path) -> int:
    return int(path.stem.split("_")[0])
