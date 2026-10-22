from __future__ import annotations

from app.core.config import Settings
from app.db.repository import Repository


class AccessService:
    def __init__(self, settings: Settings, repo: Repository) -> None:
        self.settings = settings
        self.repo = repo

    def is_owner(self, user_id: int | None) -> bool:
        return bool(user_id and self.settings.owner_id == user_id)

    async def is_allowed(self, user_id: int | None) -> bool:
        if user_id is None:
            return False
        return self.is_owner(user_id) or await self.repo.is_allowed_user(user_id)
