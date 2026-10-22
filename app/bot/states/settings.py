from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    waiting_for_allowed_domains = State()
    waiting_for_blocked_domains = State()
    waiting_for_file_limit = State()
