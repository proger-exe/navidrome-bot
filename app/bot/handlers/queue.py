from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.handlers.common import deny_if_needed, main_keyboard
from app.bot.keyboards.reply import BTN_MY_TASKS, BTN_QUEUE, BTN_STATUS
from app.core.config import Settings
from app.db.repository import Repository
from app.services.access import AccessService
from app.services.status import queue_text, status_text

router = Router()


@router.message(Command("status"))
@router.message(F.text == BTN_STATUS)
async def status(message: Message, access: AccessService, repo: Repository, settings: Settings) -> None:
    if await deny_if_needed(message, access):
        return
    await message.answer(await status_text(repo, settings.incoming_dir, settings.tmp_dir), reply_markup=main_keyboard(message, access))


@router.message(Command("queue"))
@router.message(F.text.in_({BTN_QUEUE, BTN_MY_TASKS}))
async def queue(message: Message, access: AccessService, repo: Repository, settings: Settings) -> None:
    if await deny_if_needed(message, access):
        return
    user_id = message.from_user.id
    only_user = None if access.is_owner(user_id) and message.text != BTN_MY_TASKS else user_id
    await message.answer(queue_text(await repo.list_tasks(user_id=only_user)), reply_markup=main_keyboard(message, access))


@router.message(Command("cancel"))
async def cancel(message: Message, access: AccessService, repo: Repository, settings: Settings) -> None:
    if await deny_if_needed(message, access):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /cancel <task_id>")
        return
    ok = await repo.cancel_task(int(parts[1]), message.from_user.id, settings.owner_id)
    await message.answer("Задача отменена." if ok else "Не удалось отменить задачу.")
