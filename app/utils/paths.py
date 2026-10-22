from __future__ import annotations

from pathlib import Path

from app.core.config import Settings


def ensure_runtime_dirs(settings: Settings) -> None:
    for path in [settings.incoming_dir, settings.library_dir, settings.tmp_dir, settings.data_dir, settings.log_dir]:
        path.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
