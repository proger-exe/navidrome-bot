from __future__ import annotations

from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _csv(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [item.strip() for item in value.split(",") if item.strip()]


def _ids(value: str | list[int] | None) -> list[int]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [int(item) for item in value]
    return [int(item.strip()) for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(default="", alias="BOT_TOKEN")
    owner_id: int | None = Field(default=None, alias="OWNER_ID")
    allowed_user_ids: Annotated[list[int], NoDecode] = Field(default_factory=list, alias="ALLOWED_USER_IDS")

    incoming_dir: Path = Field(default=Path("/srv/music/incoming"), alias="INCOMING_DIR")
    library_dir: Path = Field(default=Path("/srv/music/library"), alias="LIBRARY_DIR")
    tmp_dir: Path = Field(default=Path("/srv/music/tmp"), alias="TMP_DIR")
    data_dir: Path = Field(default=Path("/srv/music/bot-data"), alias="DATA_DIR")
    database_path: Path = Field(default=Path("/srv/music/bot-data/bot.db"), alias="DATABASE_PATH")
    log_dir: Path = Field(default=Path("/srv/music/bot-data/logs"), alias="LOG_DIR")

    max_file_size_mb: int = Field(default=200, alias="MAX_FILE_SIZE_MB")
    max_tasks_per_user: int = Field(default=5, alias="MAX_TASKS_PER_USER")

    ytdlp_allowed_domains: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["youtube.com", "youtu.be", "soundcloud.com", "bandcamp.com", "archive.org"],
        alias="YTDLP_ALLOWED_DOMAINS",
    )
    ytdlp_blocked_domains: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["spotify.com", "music.apple.com", "deezer.com", "tidal.com"],
        alias="YTDLP_BLOCKED_DOMAINS",
    )

    beet_bin: str = Field(default="/opt/music-bot/.venv/bin/beet", alias="BEET_BIN")
    ytdlp_bin: str = Field(default="/opt/music-bot/.venv/bin/yt-dlp", alias="YTDLP_BIN")
    ffmpeg_bin: str = Field(default="/usr/bin/ffmpeg", alias="FFMPEG_BIN")
    beets_config_path: Path = Field(default=Path("/opt/music-bot/config/beets/config.yaml"), alias="BEETS_CONFIG_PATH")

    auto_import: bool = Field(default=True, alias="AUTO_IMPORT")
    import_after_download: bool = Field(default=True, alias="IMPORT_AFTER_DOWNLOAD")
    navidrome_autoscan: bool = Field(default=True, alias="NAVIDROME_AUTOSCAN")

    @field_validator("allowed_user_ids", mode="before")
    @classmethod
    def parse_allowed_user_ids(cls, value: str | list[int] | None) -> list[int]:
        return _ids(value)

    @field_validator("ytdlp_allowed_domains", "ytdlp_blocked_domains", mode="before")
    @classmethod
    def parse_domains(cls, value: str | list[str] | None) -> list[str]:
        return [domain.lower() for domain in _csv(value)]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


def load_settings() -> Settings:
    load_dotenv()
    return Settings()
