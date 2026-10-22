from __future__ import annotations

import shutil
from pathlib import Path

from aiogram import F, Bot, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.bot.handlers.common import deny_if_needed
from app.bot.keyboards.reply import BTN_UPLOAD
from app.bot.states.upload import UploadStates
from app.core.config import Settings
from app.db.models import TaskType
from app.db.repository import Repository
from app.services.access import AccessService
from app.utils.files import ensure_inside, is_safe_audio_name, normalize_filename

router = Router()


@router.message(F.text == BTN_UPLOAD)
async def ask_file(message: Message, state: FSMContext, access: AccessService) -> None:
    if await deny_if_needed(message, access):
        return
    await state.set_state(UploadStates.waiting_for_audio_file)
    await message.answer("Отправь аудиофайл одним сообщением.")


@router.message(UploadStates.waiting_for_audio_file)
async def receive_file(message: Message, state: FSMContext, bot: Bot, access: AccessService, repo: Repository, settings: Settings) -> None:
    if await deny_if_needed(message, access):
        return
    audio = message.audio or message.document
    if audio is None:
        await message.answer("Нужен аудиофайл одним сообщением.")
        return
    filename = normalize_filename(audio.file_name or f"{audio.file_id}.mp3")
    if not is_safe_audio_name(filename):
        await message.answer("Поддерживаются только аудиофайлы.")
        return
    max_mb = await repo.max_file_size_mb(settings.max_file_size_mb)
    if audio.file_size and audio.file_size > max_mb * 1024 * 1024:
        await message.answer(f"Файл больше лимита {max_mb} МБ.")
        return
    if await repo.active_count(message.from_user.id) >= settings.max_tasks_per_user:
        await message.answer("Слишком много активных задач.")
        return
    settings.tmp_dir.mkdir(parents=True, exist_ok=True)
    settings.incoming_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = ensure_inside(settings.tmp_dir / f"{audio.file_id}_{filename}", settings.tmp_dir)
    final_path = ensure_inside(settings.incoming_dir / filename, settings.incoming_dir)
    await bot.download(audio, destination=tmp_path)
    shutil.move(str(tmp_path), str(final_path))
    task = await repo.create_task(
        message.from_user.id,
        TaskType.FILE_UPLOAD,
        original_filename=filename,
        local_path=str(Path(final_path)),
    )
    await state.clear()
    await message.answer(f"Файл принят.\n\nЗадача: #{task.id}\nСтатус: queued")
