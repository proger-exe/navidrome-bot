from __future__ import annotations

from pathlib import Path

from app.services.cleanup import cleanup_tmp


def test_cleanup_tmp_only_removes_tmp_contents(tmp_path: Path) -> None:
    tmp_dir = tmp_path / "tmp"
    keep_dir = tmp_path / "incoming"
    tmp_dir.mkdir()
    keep_dir.mkdir()
    (tmp_dir / "a.tmp").write_text("x")
    (keep_dir / "song.mp3").write_text("x")

    assert cleanup_tmp(tmp_dir) == 1
    assert not (tmp_dir / "a.tmp").exists()
    assert (keep_dir / "song.mp3").exists()
