from __future__ import annotations

from aiogram.types import Message

from app.bot.keyboards.reply import no_keyboard, owner_keyboard, user_keyboard
from app.services.access import AccessService


async def deny_if_needed(message: Message, access: AccessService) -> bool:
    if not await access.is_allowed(message.from_user.id if message.from_user else None):
        await message.answer("Нет доступа.", reply_markup=no_keyboard())
        return True
    return False


def main_keyboard(message: Message, access: AccessService):
    user_id = message.from_user.id if message.from_user else None
    return owner_keyboard() if access.is_owner(user_id) else user_keyboard()
