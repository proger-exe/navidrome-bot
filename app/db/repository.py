from __future__ import annotations

from app.core.config import Settings
from app.db.models import Task, TaskStatus, TaskType
from app.db.sqlite import Database


def _task(row) -> Task:
    return Task(**dict(row))


class Repository:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def seed(self, settings: Settings) -> None:
        for user_id in [*(settings.allowed_user_ids), *([settings.owner_id] if settings.owner_id else [])]:
            await self.add_allowed_user(user_id)
        defaults = {
            "YTDLP_ALLOWED_DOMAINS": ",".join(settings.ytdlp_allowed_domains),
            "YTDLP_BLOCKED_DOMAINS": ",".join(settings.ytdlp_blocked_domains),
            "MAX_FILE_SIZE_MB": str(settings.max_file_size_mb),
            "AUTO_IMPORT": str(settings.auto_import).lower(),
        }
        for key, value in defaults.items():
            await self.db.execute("INSERT OR IGNORE INTO settings(key, value) VALUES(?, ?)", (key, value))
        await self.db.commit()

    async def add_allowed_user(self, telegram_user_id: int) -> None:
        await self.db.execute(
            "INSERT OR IGNORE INTO allowed_users(telegram_user_id) VALUES(?)",
            (telegram_user_id,),
        )
        await self.db.commit()

    async def remove_allowed_user(self, telegram_user_id: int) -> None:
        await self.db.execute("DELETE FROM allowed_users WHERE telegram_user_id = ?", (telegram_user_id,))
        await self.db.commit()

    async def is_allowed_user(self, telegram_user_id: int) -> bool:
        row = await self.db.execute_fetchall(
            "SELECT 1 FROM allowed_users WHERE telegram_user_id = ?",
            (telegram_user_id,),
        )
        return bool(row)

    async def list_allowed_users(self) -> list[int]:
        rows = await self.db.execute_fetchall("SELECT telegram_user_id FROM allowed_users ORDER BY telegram_user_id")
        return [int(row["telegram_user_id"]) for row in rows]

    async def get_setting(self, key: str, default: str = "") -> str:
        rows = await self.db.execute_fetchall("SELECT value FROM settings WHERE key = ?", (key,))
        return str(rows[0]["value"]) if rows else default

    async def set_setting(self, key: str, value: str) -> None:
        await self.db.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await self.db.commit()

    async def domains(self, key: str) -> list[str]:
        value = await self.get_setting(key)
        return [item.strip().lower() for item in value.split(",") if item.strip()]

    async def auto_import(self) -> bool:
        return (await self.get_setting("AUTO_IMPORT", "true")).lower() in {"1", "true", "yes", "on"}

    async def max_file_size_mb(self, fallback: int) -> int:
        value = await self.get_setting("MAX_FILE_SIZE_MB", str(fallback))
        try:
            return int(value)
        except ValueError:
            return fallback

    async def create_task(
        self,
        telegram_user_id: int,
        task_type: TaskType,
        *,
        source_url: str | None = None,
        original_filename: str | None = None,
        local_path: str | None = None,
    ) -> Task:
        cursor = await self.db.execute(
            """
            INSERT INTO tasks(telegram_user_id, type, status, source_url, original_filename, local_path)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (telegram_user_id, task_type.value, TaskStatus.QUEUED.value, source_url, original_filename, local_path),
        )
        await self.db.commit()
        task = await self.get_task(int(cursor.lastrowid))
        assert task is not None
        return task

    async def get_task(self, task_id: int) -> Task | None:
        rows = await self.db.execute_fetchall("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return _task(rows[0]) if rows else None

    async def next_queued_task(self) -> Task | None:
        rows = await self.db.execute_fetchall(
            "SELECT * FROM tasks WHERE status = ? ORDER BY id LIMIT 1",
            (TaskStatus.QUEUED.value,),
        )
        return _task(rows[0]) if rows else None

    async def set_task_status(self, task_id: int, status: TaskStatus, error_message: str | None = None) -> None:
        started = ", started_at = COALESCE(started_at, CURRENT_TIMESTAMP)" if status != TaskStatus.QUEUED else ""
        finished = ", finished_at = CURRENT_TIMESTAMP" if status in {TaskStatus.DONE, TaskStatus.FAILED, TaskStatus.CANCELLED} else ""
        await self.db.execute(
            f"UPDATE tasks SET status = ?, error_message = COALESCE(?, error_message){started}{finished} WHERE id = ?",
            (status.value, error_message, task_id),
        )
        await self.db.commit()

    async def update_task_path(self, task_id: int, local_path: str) -> None:
        await self.db.execute("UPDATE tasks SET local_path = ? WHERE id = ?", (local_path, task_id))
        await self.db.commit()

    async def cancel_task(self, task_id: int, user_id: int, owner_id: int | None) -> bool:
        task = await self.get_task(task_id)
        if not task or task.status not in {TaskStatus.QUEUED.value}:
            return False
        if owner_id != user_id and task.telegram_user_id != user_id:
            return False
        await self.set_task_status(task_id, TaskStatus.CANCELLED)
        return True

    async def list_tasks(self, *, user_id: int | None = None, limit: int = 10) -> list[Task]:
        query = "SELECT * FROM tasks"
        params: list[object] = []
        if user_id is not None:
            query += " WHERE telegram_user_id = ?"
            params.append(user_id)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = await self.db.execute_fetchall(query, params)
        return [_task(row) for row in rows]

    async def active_count(self, user_id: int) -> int:
        active = (TaskStatus.QUEUED.value, TaskStatus.DOWNLOADING.value, TaskStatus.SAVING.value, TaskStatus.IMPORTING.value)
        placeholders = ",".join("?" for _ in active)
        rows = await self.db.execute_fetchall(
            f"SELECT COUNT(*) AS count FROM tasks WHERE telegram_user_id = ? AND status IN ({placeholders})",
            (user_id, *active),
        )
        return int(rows[0]["count"])

    async def status_counts(self) -> dict[str, int]:
        rows = await self.db.execute_fetchall("SELECT status, COUNT(*) AS count FROM tasks GROUP BY status")
        counts = {status.value: 0 for status in TaskStatus}
        counts.update({str(row["status"]): int(row["count"]) for row in rows})
        today = await self.db.execute_fetchall(
            """
            SELECT status, COUNT(*) AS count FROM tasks
            WHERE date(COALESCE(finished_at, created_at)) = date('now')
            AND status IN (?, ?)
            GROUP BY status
            """,
            (TaskStatus.DONE.value, TaskStatus.FAILED.value),
        )
        for row in today:
            counts[f"{row['status']}_today"] = int(row["count"])
        return counts
