from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    waiting_for_add_user = State()
    waiting_for_remove_user = State()
