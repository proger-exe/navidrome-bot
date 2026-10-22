from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.handlers.common import deny_if_needed
from app.bot.keyboards.reply import BTN_ALLOWED, BTN_AUTO_IMPORT, BTN_BLOCKED, BTN_LIMIT, BTN_SETTINGS, settings_keyboard
from app.bot.states.settings import SettingsStates
from app.db.repository import Repository
from app.services.access import AccessService

router = Router()


async def _owner_only(message: Message, access: AccessService) -> bool:
    if await deny_if_needed(message, access):
        return False
    if not access.is_owner(message.from_user.id):
        await message.answer("Недоступно.")
        return False
    return True


@router.message(F.text == BTN_SETTINGS)
async def settings_menu(message: Message, access: AccessService) -> None:
    if not await _owner_only(message, access):
        return
    await message.answer("Настройки.", reply_markup=settings_keyboard())


@router.message(F.text == BTN_ALLOWED)
async def ask_allowed(message: Message, state: FSMContext, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    await state.set_state(SettingsStates.waiting_for_allowed_domains)
    await message.answer("Текущий allowlist:\n" + await repo.get_setting("YTDLP_ALLOWED_DOMAINS") + "\n\nОтправь домены через запятую.")


@router.message(F.text == BTN_BLOCKED)
async def ask_blocked(message: Message, state: FSMContext, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    await state.set_state(SettingsStates.waiting_for_blocked_domains)
    await message.answer("Текущий blocklist:\n" + await repo.get_setting("YTDLP_BLOCKED_DOMAINS") + "\n\nОтправь домены через запятую.")


@router.message(F.text == BTN_LIMIT)
async def ask_limit(message: Message, state: FSMContext, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    await state.set_state(SettingsStates.waiting_for_file_limit)
    await message.answer("Текущий лимит: " + await repo.get_setting("MAX_FILE_SIZE_MB") + " МБ\n\nОтправь новый лимит в МБ.")


@router.message(F.text == BTN_AUTO_IMPORT)
async def toggle_auto_import(message: Message, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    current = await repo.auto_import()
    await repo.set_setting("AUTO_IMPORT", str(not current).lower())
    await message.answer(f"Автоимпорт: {'включён' if not current else 'выключен'}", reply_markup=settings_keyboard())


@router.message(SettingsStates.waiting_for_allowed_domains)
async def save_allowed(message: Message, state: FSMContext, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    await repo.set_setting("YTDLP_ALLOWED_DOMAINS", message.text or "")
    await state.clear()
    await message.answer("Allowlist сохранён.", reply_markup=settings_keyboard())


@router.message(SettingsStates.waiting_for_blocked_domains)
async def save_blocked(message: Message, state: FSMContext, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    await repo.set_setting("YTDLP_BLOCKED_DOMAINS", message.text or "")
    await state.clear()
    await message.answer("Blocklist сохранён.", reply_markup=settings_keyboard())


@router.message(SettingsStates.waiting_for_file_limit)
async def save_limit(message: Message, state: FSMContext, access: AccessService, repo: Repository) -> None:
    if not await _owner_only(message, access):
        return
    value = (message.text or "").strip()
    if not value.isdigit() or int(value) < 1:
        await message.answer("Нужен положительный лимит в МБ.")
        return
    await repo.set_setting("MAX_FILE_SIZE_MB", value)
    await state.clear()
    await message.answer("Лимит сохранён.", reply_markup=settings_keyboard())
