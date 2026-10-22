from __future__ import annotations

from pathlib import Path

from app.db.models import Task
from app.db.repository import Repository


def _file_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.iterdir() if item.is_file())


async def status_text(repo: Repository, incoming_dir: Path, tmp_dir: Path) -> str:
    counts = await repo.status_counts()
    return (
        "Система: online\n\n"
        "Очередь:\n"
        f"- queued: {counts.get('queued', 0)}\n"
        f"- downloading: {counts.get('downloading', 0)}\n"
        f"- importing: {counts.get('importing', 0)}\n"
        f"- done today: {counts.get('done_today', 0)}\n"
        f"- failed today: {counts.get('failed_today', 0)}\n\n"
        "Папки:\n"
        f"- incoming: {_file_count(incoming_dir)} файлов\n"
        f"- tmp: {_file_count(tmp_dir)} файлов"
    )


def queue_text(tasks: list[Task]) -> str:
    if not tasks:
        return "Очередь пуста."
    lines = ["Очередь:"]
    for task in tasks:
        source = "URL" if task.source_url else "file upload"
        if task.type == "manual_import":
            source = "manual import"
        if task.type == "cleanup_tmp":
            source = "cleanup tmp"
        lines.append(f"\n#{task.id} {task.status}\nИсточник: {source}")
    return "\n".join(lines)
