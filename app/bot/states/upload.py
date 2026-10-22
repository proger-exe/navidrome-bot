from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class UploadStates(StatesGroup):
    waiting_for_audio_file = State()
    waiting_for_url = State()
