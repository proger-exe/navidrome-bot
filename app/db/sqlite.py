from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  telegram_user_id INTEGER NOT NULL,
  type TEXT NOT NULL,
  status TEXT NOT NULL,
  source_url TEXT,
  original_filename TEXT,
  local_path TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  started_at TEXT,
  finished_at TEXT
);

CREATE TABLE IF NOT EXISTS allowed_users (
  telegram_user_id INTEGER PRIMARY KEY,
  added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(telegram_user_id);
"""


class Cursor:
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self.lastrowid = cursor.lastrowid


class Database:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    async def execute(self, sql: str, params: object = ()) -> Cursor:
        return Cursor(self.connection.execute(sql, params))

    async def execute_fetchall(self, sql: str, params: object = ()) -> list[sqlite3.Row]:
        return list(self.connection.execute(sql, params).fetchall())

    async def executescript(self, sql: str) -> None:
        self.connection.executescript(sql)

    async def commit(self) -> None:
        self.connection.commit()

    async def close(self) -> None:
        self.connection.close()


async def connect(database_path: Path) -> Database:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    db = Database(sqlite3.connect(database_path))
    await db.executescript(SCHEMA)
    await db.commit()
    return db
