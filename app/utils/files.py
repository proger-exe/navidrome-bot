from __future__ import annotations

import re
import unicodedata
from pathlib import Path


SAFE_EXTENSIONS = {".mp3", ".flac", ".m4a", ".ogg", ".opus", ".wav", ".aac", ".alac"}


def normalize_filename(filename: str) -> str:
    name = Path(filename).name
    normalized = unicodedata.normalize("NFKC", name)
    normalized = re.sub(r"[^\w.\- ()\[\]]+", "_", normalized, flags=re.UNICODE).strip(" .")
    return normalized or "audio"


def is_safe_audio_name(filename: str) -> bool:
    return Path(filename).suffix.lower() in SAFE_EXTENSIONS


def ensure_inside(path: Path, root: Path) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ValueError("path outside allowed directory")
    return resolved_path
