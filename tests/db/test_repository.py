from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import Settings
from app.db.models import TaskStatus, TaskType
from app.db.repository import Repository
from app.db.sqlite import connect


@pytest.mark.asyncio
async def test_repository_seed_and_tasks(tmp_path: Path) -> None:
    settings = Settings(
        BOT_TOKEN="token",
        OWNER_ID="1",
        ALLOWED_USER_IDS="2",
        DATABASE_PATH=str(tmp_path / "bot.db"),
    )
    db = await connect(settings.database_path)
    repo = Repository(db)

    await repo.seed(settings)
    assert await repo.is_allowed_user(1)
    assert await repo.is_allowed_user(2)

    task = await repo.create_task(2, TaskType.URL_DOWNLOAD, source_url="https://youtu.be/a")
    assert task.status == TaskStatus.QUEUED.value
    assert await repo.active_count(2) == 1

    await repo.set_task_status(task.id, TaskStatus.DONE)
    counts = await repo.status_counts()
    assert counts["done"] == 1

    await db.close()
