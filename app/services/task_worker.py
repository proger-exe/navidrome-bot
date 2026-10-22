from __future__ import annotations

import asyncio
import logging

from aiogram import Bot

from app.db.models import Task, TaskStatus, TaskType
from app.db.repository import Repository
from app.services.downloader import Downloader
from app.services.importer import Importer

logger = logging.getLogger(__name__)


class TaskWorker:
    def __init__(self, repo: Repository, downloader: Downloader, importer: Importer, bot: Bot | None = None) -> None:
        self.repo = repo
        self.downloader = downloader
        self.importer = importer
        self.bot = bot
        self._running = False

    async def run_forever(self) -> None:
        self._running = True
        logger.info("task worker started")
        while self._running:
            task = await self.repo.next_queued_task()
            if task is None:
                await asyncio.sleep(2)
                continue
            await self.process(task)

    def stop(self) -> None:
        self._running = False

    async def process(self, task: Task) -> None:
        try:
            if task.type == TaskType.URL_DOWNLOAD.value:
                await self._process_url(task)
            elif task.type in {TaskType.FILE_UPLOAD.value, TaskType.MANUAL_IMPORT.value}:
                await self._process_import(task)
            else:
                await self.repo.set_task_status(task.id, TaskStatus.DONE)
        except Exception as exc:  # noqa: BLE001
            logger.exception("task failed id=%s", task.id)
            await self.repo.set_task_status(task.id, TaskStatus.FAILED, str(exc))
            await self._notify(task.telegram_user_id, f"Задача #{task.id} завершилась с ошибкой.\nПодробности записаны в лог.")

    async def _process_url(self, task: Task) -> None:
        assert task.source_url
        await self.repo.set_task_status(task.id, TaskStatus.DOWNLOADING)
        result = await self.downloader.download_audio(task.source_url)
        if result.returncode != 0:
            await self.repo.set_task_status(task.id, TaskStatus.FAILED, result.stderr[-1000:])
            await self._notify(task.telegram_user_id, f"Скачивание завершилось с ошибкой.\nЗадача: #{task.id}")
            return
        await self.repo.set_task_status(task.id, TaskStatus.DOWNLOADED)
        await self._process_import(task)

    async def _process_import(self, task: Task) -> None:
        await self.repo.set_task_status(task.id, TaskStatus.IMPORTING)
        result = await self.importer.import_incoming()
        if result.returncode != 0:
            await self.repo.set_task_status(task.id, TaskStatus.FAILED, result.stderr[-1000:])
            await self._notify(task.telegram_user_id, f"Импорт завершился с ошибкой.\nЗадача: #{task.id}")
            return
        await self.repo.set_task_status(task.id, TaskStatus.DONE)
        await self._notify(task.telegram_user_id, f"Импорт завершён.\n\nЗадача: #{task.id}\nСтатус: done")

    async def _notify(self, user_id: int, text: str) -> None:
        if self.bot is not None:
            await self.bot.send_message(user_id, text)
