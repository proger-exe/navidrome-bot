from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.handlers.common import deny_if_needed
from app.bot.keyboards.reply import BTN_URL
from app.bot.states.upload import UploadStates
from app.core.config import Settings
from app.db.models import TaskType
from app.db.repository import Repository
from app.services.access import AccessService
from app.utils.urls import is_allowed_url

router = Router()


@router.message(F.text == BTN_URL)
async def ask_url(message: Message, state: FSMContext, access: AccessService) -> None:
    if await deny_if_needed(message, access):
        return
    await state.set_state(UploadStates.waiting_for_url)
    await message.answer("Отправь ссылку на разрешённый источник.")


@router.message(UploadStates.waiting_for_url)
async def receive_url(message: Message, state: FSMContext, access: AccessService, repo: Repository, settings: Settings) -> None:
    if await deny_if_needed(message, access):
        return
    url = (message.text or "").strip()
    allowed = await repo.domains("YTDLP_ALLOWED_DOMAINS")
    blocked = await repo.domains("YTDLP_BLOCKED_DOMAINS")
    if not is_allowed_url(url, allowed, blocked):
        await message.answer("Источник не поддерживается.\nМожно загрузить собственный или купленный аудиофайл напрямую.")
        return
    if await repo.active_count(message.from_user.id) >= settings.max_tasks_per_user:
        await message.answer("Слишком много активных задач.")
        return
    task = await repo.create_task(message.from_user.id, TaskType.URL_DOWNLOAD, source_url=url)
    await state.clear()
    await message.answer(f"Ссылка принята.\n\nЗадача: #{task.id}\nСтатус: queued")
