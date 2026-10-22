from __future__ import annotations

import logging

from app.core.config import Settings
from app.utils.subprocess import CommandResult, run_exec

logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def download_audio(self, url: str) -> CommandResult:
        output_template = str(self.settings.incoming_dir / "%(artist,uploader|Unknown Artist)s" / "%(title)s.%(ext)s")
        result = await run_exec(
            self.settings.ytdlp_bin,
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",
            "--embed-thumbnail",
            "--add-metadata",
            "-o",
            output_template,
            url,
        )
        logger.info("yt-dlp finished rc=%s stdout=%s stderr=%s", result.returncode, result.stdout, result.stderr)
        return result
