from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

BTN_UPLOAD = "🎵 Загрузить музыку"
BTN_URL = "🔗 Скачать по ссылке"
BTN_IMPORT = "📥 Импортировать"
BTN_STATUS = "📊 Статус"
BTN_QUEUE = "📋 Очередь"
BTN_MY_TASKS = "📋 Мои задачи"
BTN_CLEANUP = "🧹 Очистить tmp"
BTN_USERS = "👥 Пользователи"
BTN_SETTINGS = "⚙️ Настройки"
BTN_LOGS = "📜 Логи"
BTN_HELP = "❓ Помощь"
BTN_ADD_USER = "➕ Добавить пользователя"
BTN_REMOVE_USER = "➖ Удалить пользователя"
BTN_LIST_USERS = "📃 Список пользователей"
BTN_ALLOWED = "🌐 Allowlist доменов"
BTN_BLOCKED = "🚫 Blocklist доменов"
BTN_LIMIT = "📦 Лимит файла"
BTN_AUTO_IMPORT = "🔁 Автоимпорт"
BTN_BACK = "⬅️ Назад"


def owner_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_UPLOAD), KeyboardButton(text=BTN_URL)],
            [KeyboardButton(text=BTN_IMPORT), KeyboardButton(text=BTN_STATUS)],
            [KeyboardButton(text=BTN_QUEUE), KeyboardButton(text=BTN_CLEANUP)],
            [KeyboardButton(text=BTN_USERS), KeyboardButton(text=BTN_SETTINGS)],
            [KeyboardButton(text=BTN_LOGS)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def user_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_UPLOAD), KeyboardButton(text=BTN_URL)],
            [KeyboardButton(text=BTN_STATUS), KeyboardButton(text=BTN_MY_TASKS)],
            [KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def users_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ADD_USER), KeyboardButton(text=BTN_REMOVE_USER)],
            [KeyboardButton(text=BTN_LIST_USERS)],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def settings_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ALLOWED), KeyboardButton(text=BTN_BLOCKED)],
            [KeyboardButton(text=BTN_LIMIT), KeyboardButton(text=BTN_AUTO_IMPORT)],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def no_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
