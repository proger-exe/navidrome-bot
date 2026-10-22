from __future__ import annotations

from pathlib import Path

import pytest

from app.utils.files import ensure_inside, is_safe_audio_name, normalize_filename


def test_normalize_filename_strips_paths() -> None:
    assert normalize_filename("../../Track?.mp3") == "Track_.mp3"
    assert normalize_filename("   ") == "audio"


def test_safe_audio_extensions() -> None:
    assert is_safe_audio_name("song.flac")
    assert not is_safe_audio_name("song.exe")


def test_ensure_inside_blocks_traversal(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    assert ensure_inside(root / "song.mp3", root) == (root / "song.mp3").resolve()
    with pytest.raises(ValueError):
        ensure_inside(tmp_path / "outside.mp3", root)
