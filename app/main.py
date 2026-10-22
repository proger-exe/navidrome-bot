from __future__ import annotations

import argparse
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import setup_routers
from app.core.config import load_settings
from app.core.logging import setup_logging
from app.db.repository import Repository
from app.db.sqlite import connect
from app.services.access import AccessService
from app.services.downloader import Downloader
from app.services.importer import Importer
from app.services.task_worker import TaskWorker
from app.utils.paths import ensure_runtime_dirs

logger = logging.getLogger(__name__)


async def build_dispatcher(bot: Bot | None = None) -> tuple[Dispatcher, TaskWorker]:
    settings = load_settings()
    ensure_runtime_dirs(settings)
    setup_logging(settings)
    db = await connect(settings.database_path)
    repo = Repository(db)
    await repo.seed(settings)
    access = AccessService(settings, repo)
    downloader = Downloader(settings)
    importer = Importer(settings)
    worker = TaskWorker(repo, downloader, importer, bot)

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(setup_routers())
    dp["settings"] = settings
    dp["repo"] = repo
    dp["access"] = access
    dp["downloader"] = downloader
    dp["importer"] = importer
    dp["worker"] = worker
    return dp, worker


async def run_bot() -> None:
    settings = load_settings()
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required")
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp, worker = await build_dispatcher(bot)
    worker_task = asyncio.create_task(worker.run_forever())
    try:
        logger.info("bot polling started")
        await dp.start_polling(bot)
    finally:
        worker.stop()
        worker_task.cancel()
        await bot.session.close()


async def check_config() -> None:
    settings = load_settings()
    ensure_runtime_dirs(settings)
    db = await connect(settings.database_path)
    repo = Repository(db)
    await repo.seed(settings)
    await db.close()
    print("config ok")


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Import Bot")
    parser.add_argument("--check-config", action="store_true", help="validate config and initialize SQLite")
    args = parser.parse_args()
    asyncio.run(check_config() if args.check_config else run_bot())


if __name__ == "__main__":
    main()
