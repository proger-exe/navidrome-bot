from __future__ import annotations

from pathlib import Path


def tail_log(log_dir: Path, lines: int = 40) -> str:
    log_file = log_dir / "music-bot.log"
    if not log_file.exists():
        return "Лог пока пуст."
    content = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(content[-lines:]) or "Лог пока пуст."
