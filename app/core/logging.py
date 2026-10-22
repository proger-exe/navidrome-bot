from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from app.core.config import Settings


def setup_logging(settings: Settings) -> None:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    log_file = settings.log_dir / "music-bot.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=5, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
