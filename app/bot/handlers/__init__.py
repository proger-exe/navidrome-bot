from __future__ import annotations

from aiogram import Router

from app.bot.handlers import admin, files, queue, settings, start, urls


def setup_routers() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(files.router)
    router.include_router(urls.router)
    router.include_router(queue.router)
    router.include_router(admin.router)
    router.include_router(settings.router)
    return router
