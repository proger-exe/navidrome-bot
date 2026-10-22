from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TaskType(str, Enum):
    FILE_UPLOAD = "file_upload"
    URL_DOWNLOAD = "url_download"
    MANUAL_IMPORT = "manual_import"
    CLEANUP_TMP = "cleanup_tmp"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    SAVING = "saving"
    IMPORTING = "importing"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Task:
    id: int
    telegram_user_id: int
    type: str
    status: str
    source_url: str | None = None
    original_filename: str | None = None
    local_path: str | None = None
    error_message: str | None = None
    created_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
