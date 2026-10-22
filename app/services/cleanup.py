from __future__ import annotations

from pathlib import Path

from app.utils.files import ensure_inside


def cleanup_tmp(tmp_dir: Path) -> int:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    deleted = 0
    for path in sorted(tmp_dir.rglob("*"), reverse=True):
        ensure_inside(path, tmp_dir)
        if path.is_file() or path.is_symlink():
            path.unlink()
            deleted += 1
        elif path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass
    return deleted
