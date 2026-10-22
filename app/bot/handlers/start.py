from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.handlers.common import deny_if_needed, main_keyboard
from app.bot.keyboards.reply import BTN_BACK, BTN_HELP
from app.services.access import AccessService

router = Router()


@router.message(Command("start"))
async def start(message: Message, access: AccessService) -> None:
    if await deny_if_needed(message, access):
        return
    await message.answer("Выбери действие.", reply_markup=main_keyboard(message, access))


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def help_message(message: Message, access: AccessService) -> None:
    if await deny_if_needed(message, access):
        return
    await message.answer(
        "Можно загрузить аудиофайл, отправить ссылку на разрешённый источник, посмотреть статус и очередь.",
        reply_markup=main_keyboard(message, access),
    )


@router.message(F.text == BTN_BACK)
async def back(message: Message, access: AccessService) -> None:
    if await deny_if_needed(message, access):
        return
    await message.answer("Главное меню.", reply_markup=main_keyboard(message, access))
