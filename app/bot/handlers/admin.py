from __future__ import annotations

from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.handlers.common import deny_if_needed, main_keyboard
from app.bot.keyboards.reply import BTN_ADD_USER, BTN_CLEANUP, BTN_IMPORT, BTN_LIST_USERS, BTN_LOGS, BTN_REMOVE_USER, BTN_USERS, users_keyboard
from app.bot.states.users import UserStates
from app.core.config import Settings
from app.db.models import TaskStatus, TaskType
from app.db.repository import Repository
from app.services.access import AccessService
from app.services.cleanup import cleanup_tmp
from app.services.logs import tail_log

router = Router()


async def _owner_only(message: Message, access: AccessService) -> bool:
    if await deny_if_needed(message, access):
        return False
    if not access.is_owner(message.from_user.id):
        await message.answer("Недоступно.")
        return False
    return True


@router.message(F.text == BTN_USERS)
async def users_menu(message: Message, access: AccessService) -> None:
    if not await _owner_only(message, access):
        return
    await message.answer("Пользователи.", reply_markup=users_keyboard())


@router.message(F.text == BTN_ADD_USER)
async def ask_add_user(message: Message, state: FSMContext, access: AccessService) -> None:
    if not await _owner_only(message, access):
        return
    await state.set_state(UserStates.waiting_for_add_user)
    await message.answer("Отправь Telegram ID пользователя.")


@router.message(F.text == BTN_REMOVE_USER)
async def ask_remove_user(message: Message, state: FSMContext, access: AccessService) -> None:
    if not await _owner_only(message, access):
        return
    await state.set_state(UserStates.waiting_for_remove_user)
    await message.answer("Отправь Telegram ID пользователя.")


@router.message(UserStates.waiting_for_add_user)
async def add_user_state(message: Message, state: FSMContext, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    if not (message.text or "").strip().isdigit():
        await message.answer("Нужен числовой Telegram ID.")
        return
    await repo.add_allowed_user(int(message.text.strip()))
    await state.clear()
    await message.answer("Пользователь добавлен.", reply_markup=users_keyboard())


@router.message(UserStates.waiting_for_remove_user)
async def remove_user_state(message: Message, state: FSMContext, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    if not (message.text or "").strip().isdigit():
        await message.answer("Нужен числовой Telegram ID.")
        return
    await repo.remove_allowed_user(int(message.text.strip()))
    await state.clear()
    await message.answer("Пользователь удалён.", reply_markup=users_keyboard())


@router.message(Command("allow"))
async def allow_user(message: Message, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /allow <telegram_id>")
        return
    await repo.add_allowed_user(int(parts[1]))
    await message.answer("Пользователь добавлен.")


@router.message(Command("deny"))
async def deny_user(message: Message, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /deny <telegram_id>")
        return
    await repo.remove_allowed_user(int(parts[1]))
    await message.answer("Пользователь удалён.")


@router.message(F.text == BTN_LIST_USERS)
async def list_users(message: Message, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    users = await repo.list_allowed_users()
    await message.answer("Пользователи:\n" + "\n".join(str(user) for user in users))


@router.message(Command("import"))
@router.message(F.text == BTN_IMPORT)
async def manual_import(message: Message, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    task = await repo.create_task(message.from_user.id, TaskType.MANUAL_IMPORT)
    await message.answer(f"Запускаю импорт из /srv/music/incoming.\n\nЗадача: #{task.id}")


@router.message(F.text == BTN_CLEANUP)
async def cleanup(message: Message, access: AccessService, settings: Settings, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    task = await repo.create_task(message.from_user.id, TaskType.CLEANUP_TMP)
    deleted = cleanup_tmp(settings.tmp_dir)
    await repo.update_task_path(task.id, str(settings.tmp_dir))
    await repo.set_task_status(task.id, TaskStatus.DONE)
    await message.answer(f"tmp очищен.\nУдалено файлов: {deleted}", reply_markup=main_keyboard(message, access))


@router.message(Command("logs"))
@router.message(F.text == BTN_LOGS)
async def logs(message: Message, access: AccessService, settings: Settings) -> None:
    if not await _owner_only(message, access):
        return
    text = tail_log(settings.log_dir)
    await message.answer(f"<pre>{escape(text[-3500:])}</pre>", parse_mode="HTML")
