# Техническое задание: Music Import Bot для Navidrome без Docker

## 1. Название проекта

**Music Import Bot**

## 2. Цель проекта

Разработать Telegram-бота для загрузки музыки в self-hosted библиотеку Navidrome.

Бот должен позволять через Telegram:

1. загружать аудиофайлы;
2. отправлять ссылки на разрешённые источники;
3. скачивать аудио через `yt-dlp`;
4. складывать файлы во входящую папку;
5. запускать импорт через `beets`;
6. смотреть очередь задач;
7. получать статус обработки;
8. управлять ботом через ReplyKeyboard-интерфейс.

Проект разворачивается **без Docker**, напрямую на сервере через:

```text
Python venv
systemd
host directories
beets
yt-dlp
ffmpeg
```

## 3. Общая архитектура

```text
Telegram
   ↓
Aiogram Bot
   ↓
ReplyKeyboard UI
   ↓
Task Queue
   ↓
Download / Upload Handler
   ↓
/srv/music/incoming
   ↓
beets import
   ↓
/srv/music/library
   ↓
Navidrome
```

## 4. Основной стек

### Backend

* Python 3.12+
* aiogram 3.x
* pydantic v2
* python-dotenv
* aiofiles
* aiosqlite или Tortoise ORM
* SQLite для MVP
* APScheduler или собственный background worker
* yt-dlp
* beets
* ffmpeg

### Deployment

* без Docker;
* запуск через `systemd`;
* код проекта в `/opt/music-bot`;
* виртуальное окружение в `/opt/music-bot/.venv`;
* данные в `/srv/music`.

## 5. Основные директории

```text
/opt/music-bot
```

Код проекта.

```text
/opt/music-bot/.venv
```

Python virtual environment.

```text
/srv/music/incoming
```

Папка для новых файлов и скачанных треков.

```text
/srv/music/library
```

Основная библиотека Navidrome.

```text
/srv/music/tmp
```

Временные файлы скачивания.

```text
/srv/music/bot-data
```

База данных, логи и служебные файлы бота.

```text
/srv/music/beets
```

База beets.

## 6. Установка зависимостей на сервер

### 6.1. Системные зависимости

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip ffmpeg
```

### 6.2. Создание директорий

```bash
sudo mkdir -p /opt/music-bot
sudo mkdir -p /srv/music/incoming
sudo mkdir -p /srv/music/library
sudo mkdir -p /srv/music/tmp
sudo mkdir -p /srv/music/bot-data
sudo mkdir -p /srv/music/beets

sudo chown -R shelby:shelby /opt/music-bot
sudo chown -R shelby:shelby /srv/music
```

### 6.3. Python venv

```bash
cd /opt/music-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
```

### 6.4. Python зависимости

```bash
pip install aiogram python-dotenv pydantic aiofiles aiosqlite yt-dlp beets
```

## 7. Переменные окружения

Файл:

```text
/opt/music-bot/.env
```

Пример:

```env
BOT_TOKEN=
OWNER_ID=
ALLOWED_USER_IDS=

INCOMING_DIR=/srv/music/incoming
LIBRARY_DIR=/srv/music/library
TMP_DIR=/srv/music/tmp
DATA_DIR=/srv/music/bot-data

DATABASE_PATH=/srv/music/bot-data/bot.db
LOG_DIR=/srv/music/bot-data/logs

MAX_FILE_SIZE_MB=200
MAX_TASKS_PER_USER=5

YTDLP_ALLOWED_DOMAINS=youtube.com,youtu.be,soundcloud.com,bandcamp.com,archive.org
YTDLP_BLOCKED_DOMAINS=spotify.com,music.apple.com,deezer.com,tidal.com

BEET_BIN=/opt/music-bot/.venv/bin/beet
YTDLP_BIN=/opt/music-bot/.venv/bin/yt-dlp
FFMPEG_BIN=/usr/bin/ffmpeg

BEETS_CONFIG_PATH=/opt/music-bot/config/beets/config.yaml

AUTO_IMPORT=true
IMPORT_AFTER_DOWNLOAD=true
NAVIDROME_AUTOSCAN=true
```

## 8. Роли пользователей

### Owner

Главный пользователь бота.

Может:

* загружать файлы;
* отправлять ссылки;
* запускать импорт;
* смотреть очередь;
* отменять задачи;
* смотреть логи;
* очищать временные файлы;
* управлять пользователями;
* менять allowlist доменов.

### Allowed User

Разрешённый пользователь.

Может:

* загружать аудиофайлы;
* отправлять ссылки;
* смотреть свои задачи;
* смотреть статус.

### Unknown User

Пользователь без доступа.

При попытке использовать бота получает сообщение:

```text
Нет доступа.
```

## 9. Интерфейс через ReplyKeyboard

Бот должен использовать **ReplyKeyboardMarkup**, а не inline-only интерфейс.

Команды остаются доступными, но основной сценарий должен работать через кнопки.

## 10. Главное меню

### Для Owner

```text
🎵 Загрузить музыку
🔗 Скачать по ссылке
📥 Импортировать
📊 Статус
📋 Очередь
🧹 Очистить tmp
👥 Пользователи
⚙️ Настройки
📜 Логи
```

### Для Allowed User

```text
🎵 Загрузить музыку
🔗 Скачать по ссылке
📊 Статус
📋 Мои задачи
❓ Помощь
```

### Для Unknown User

ReplyKeyboard не показывается.

## 11. Состояния интерфейса

Для сценариев, где бот ждёт следующий ввод, использовать FSM aiogram.

### 11.1. Состояние ожидания файла

Пользователь нажимает:

```text
🎵 Загрузить музыку
```

Бот отвечает:

```text
Отправь аудиофайл одним сообщением.
```

FSM state:

```text
waiting_for_audio_file
```

После получения файла бот выходит из состояния.

### 11.2. Состояние ожидания ссылки

Пользователь нажимает:

```text
🔗 Скачать по ссылке
```

Бот отвечает:

```text
Отправь ссылку на разрешённый источник.
```

FSM state:

```text
waiting_for_url
```

После получения ссылки бот проверяет домен и создаёт задачу скачивания.

### 11.3. Состояние управления пользователями

Owner нажимает:

```text
👥 Пользователи
```

Бот показывает подменю:

```text
➕ Добавить пользователя
➖ Удалить пользователя
📃 Список пользователей
⬅️ Назад
```

### 11.4. Состояние настроек

Owner нажимает:

```text
⚙️ Настройки
```

Бот показывает подменю:

```text
🌐 Allowlist доменов
🚫 Blocklist доменов
📦 Лимит файла
🔁 Автоимпорт
⬅️ Назад
```

## 12. Команды

ReplyKeyboard является основным интерфейсом, но команды нужны как резервный способ управления.

### `/start`

Проверяет доступ и показывает главное меню.

### `/help`

Показывает справку.

### `/status`

Показывает состояние системы.

### `/queue`

Показывает очередь задач.

### `/import`

Запускает импорт вручную.

Только Owner.

### `/cancel <task_id>`

Отменяет задачу.

### `/logs`

Показывает последние строки логов.

Только Owner.

### `/allow <telegram_id>`

Добавляет пользователя.

Только Owner.

### `/deny <telegram_id>`

Удаляет пользователя.

Только Owner.

## 13. Основные сценарии

## 13.1. Загрузка аудиофайла

Пользователь нажимает:

```text
🎵 Загрузить музыку
```

Бот отвечает:

```text
Отправь аудиофайл.
```

Пользователь отправляет файл.

Бот должен:

1. проверить доступ;
2. проверить тип файла;
3. проверить размер файла;
4. скачать файл во временную папку;
5. безопасно нормализовать имя файла;
6. переместить файл в `/srv/music/incoming`;
7. создать задачу импорта;
8. если `AUTO_IMPORT=true`, запустить импорт через beets;
9. отправить итоговый статус.

Ответ после принятия:

```text
Файл принят.

Задача: #128
Статус: queued
```

Ответ после завершения:

```text
Импорт завершён.

Задача: #128
Статус: done
```

## 13.2. Скачивание по ссылке

Пользователь нажимает:

```text
🔗 Скачать по ссылке
```

Бот отвечает:

```text
Отправь ссылку.
```

Пользователь отправляет URL.

Бот должен:

1. проверить доступ;
2. распарсить URL;
3. проверить домен по allowlist;
4. проверить отсутствие домена в blocklist;
5. создать задачу;
6. скачать аудио через yt-dlp;
7. сохранить результат в `/srv/music/incoming`;
8. при необходимости запустить beets import;
9. отправить пользователю статус.

Если домен запрещён:

```text
Источник не поддерживается.
Можно загрузить собственный или купленный аудиофайл напрямую.
```

## 13.3. Ручной импорт

Owner нажимает:

```text
📥 Импортировать
```

Бот отвечает:

```text
Запускаю импорт из /srv/music/incoming.
```

Бот запускает:

```bash
beet import -q /srv/music/incoming
```

После завершения:

```text
Импорт завершён.
```

При ошибке:

```text
Импорт завершился с ошибкой.
Подробности записаны в лог.
```

## 13.4. Просмотр статуса

Пользователь нажимает:

```text
📊 Статус
```

Бот показывает:

```text
Система: online

Очередь:
- queued: 2
- downloading: 1
- importing: 0
- done today: 8
- failed today: 1

Папки:
- incoming: 4 файла
- tmp: 0 файлов
```

## 13.5. Очередь задач

Пользователь нажимает:

```text
📋 Очередь
```

Owner видит все задачи.

Allowed User видит только свои задачи.

Пример:

```text
Очередь:

#128 downloading
Источник: URL

#129 queued
Источник: file upload

#130 importing
Источник: file upload
```

## 13.6. Очистка tmp

Owner нажимает:

```text
🧹 Очистить tmp
```

Бот удаляет временные файлы из:

```text
/srv/music/tmp
```

Бот не должен удалять:

```text
/srv/music/incoming
/srv/music/library
```

Ответ:

```text
tmp очищен.
Удалено файлов: 12
```

## 14. ReplyKeyboard структура

## 14.1. Main owner keyboard

```python
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

owner_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎵 Загрузить музыку"),
            KeyboardButton(text="🔗 Скачать по ссылке"),
        ],
        [
            KeyboardButton(text="📥 Импортировать"),
            KeyboardButton(text="📊 Статус"),
        ],
        [
            KeyboardButton(text="📋 Очередь"),
            KeyboardButton(text="🧹 Очистить tmp"),
        ],
        [
            KeyboardButton(text="👥 Пользователи"),
            KeyboardButton(text="⚙️ Настройки"),
        ],
        [
            KeyboardButton(text="📜 Логи"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие"
)
```

## 14.2. User keyboard

```python
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎵 Загрузить музыку"),
            KeyboardButton(text="🔗 Скачать по ссылке"),
        ],
        [
            KeyboardButton(text="📊 Статус"),
            KeyboardButton(text="📋 Мои задачи"),
        ],
        [
            KeyboardButton(text="❓ Помощь"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие"
)
```

## 14.3. Users submenu

```python
users_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Добавить пользователя"),
            KeyboardButton(text="➖ Удалить пользователя"),
        ],
        [
            KeyboardButton(text="📃 Список пользователей"),
        ],
        [
            KeyboardButton(text="⬅️ Назад"),
        ],
    ],
    resize_keyboard=True
)
```

## 14.4. Settings submenu

```python
settings_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🌐 Allowlist доменов"),
            KeyboardButton(text="🚫 Blocklist доменов"),
        ],
        [
            KeyboardButton(text="📦 Лимит файла"),
            KeyboardButton(text="🔁 Автоимпорт"),
        ],
        [
            KeyboardButton(text="⬅️ Назад"),
        ],
    ],
    resize_keyboard=True
)
```

## 15. Очередь задач

Очередь может быть реализована:

1. через таблицу `tasks` в SQLite;
2. через in-memory worker с сохранением статусов в БД;
3. через polling задач из БД.

Для MVP достаточно одного worker-процесса внутри бота.

## 16. Модель задачи

```text
id
telegram_user_id
type
status
source_url
original_filename
local_path
error_message
created_at
started_at
finished_at
```

## 17. Типы задач

```text
file_upload
url_download
manual_import
cleanup_tmp
```

## 18. Статусы задач

```text
queued
downloading
downloaded
saving
importing
done
failed
cancelled
```

## 19. Работа с yt-dlp

Для скачивания используется `yt-dlp`.

Пример запуска:

```bash
/opt/music-bot/.venv/bin/yt-dlp \
  -x \
  --audio-format mp3 \
  --audio-quality 0 \
  --embed-thumbnail \
  --add-metadata \
  -o "/srv/music/incoming/%(artist,uploader|Unknown Artist)s/%(title)s.%(ext)s" \
  "<url>"
```

В коде запрещено запускать это через `shell=True`.

Нужно использовать:

```python
await asyncio.create_subprocess_exec(
    ytdlp_bin,
    "-x",
    "--audio-format", "mp3",
    "--audio-quality", "0",
    "--embed-thumbnail",
    "--add-metadata",
    "-o", output_template,
    url,
)
```

## 20. Работа с beets

Для импорта используется `beet import`.

MVP-команда:

```bash
/opt/music-bot/.venv/bin/beet import -q /srv/music/incoming
```

Переменная окружения:

```env
BEET_BIN=/opt/music-bot/.venv/bin/beet
```

Если используется отдельный config:

```bash
BEETSDIR=/opt/music-bot/config/beets beet import -q /srv/music/incoming
```

## 21. Конфигурация beets

Файл:

```text
/opt/music-bot/config/beets/config.yaml
```

Пример:

```yaml
directory: /srv/music/library
library: /srv/music/beets/library.db

import:
  move: yes
  write: yes
  copy: no
  timid: no

paths:
  default: $albumartist/$album%aunique{}/$track $title
  singleton: Singles/$artist/$title

plugins: fetchart embedart fromfilename
```

## 22. Интеграция с Navidrome

Для MVP бот не обязан напрямую обращаться к Navidrome.

Navidrome должен автоматически сканировать:

```text
/srv/music/library
```

Рекомендуемый режим:

```text
Navidrome Scanner.Schedule = @every 5m
```

Бот после импорта может отвечать:

```text
Файл импортирован.
Navidrome увидит его после ближайшего сканирования.
```

## 23. Логирование

Логи хранить в:

```text
/srv/music/bot-data/logs
```

Логировать:

1. запуск бота;
2. входящие сообщения;
3. отказы доступа;
4. создание задач;
5. смену статусов;
6. ошибки скачивания;
7. ошибки импорта;
8. stdout/stderr от yt-dlp;
9. stdout/stderr от beets.

## 24. Безопасность

Требования:

1. доступ только по Telegram ID;
2. неизвестным пользователям не показывать меню;
3. не запускать команды через `shell=True`;
4. проверять URL по allowlist;
5. блокировать DRM-сервисы;
6. нормализовать имена файлов;
7. запрещать path traversal;
8. ограничивать размер файлов;
9. ограничивать число активных задач;
10. не показывать внутренние пути сервера обычным пользователям;
11. полный traceback писать только в лог;
12. все операции с файлами выполнять только внутри разрешённых директорий.

## 25. systemd service

Файл:

```text
/etc/systemd/system/music-bot.service
```

Содержимое:

```ini
[Unit]
Description=Music Import Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=shelby
Group=shelby
WorkingDirectory=/opt/music-bot
EnvironmentFile=/opt/music-bot/.env
ExecStart=/opt/music-bot/.venv/bin/python -m app.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Команды управления:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now music-bot
sudo systemctl status music-bot
journalctl -u music-bot -f
```

## 26. Рекомендуемая структура проекта

```text
music-bot/
  app/
    bot/
      handlers/
        start.py
        files.py
        urls.py
        queue.py
        admin.py
        settings.py
      keyboards/
        reply.py
      middlewares/
        auth.py
      states/
        upload.py
        settings.py
        users.py
    core/
      config.py
      logging.py
    db/
      models.py
      repository.py
      sqlite.py
    services/
      downloader.py
      importer.py
      task_worker.py
      access.py
      cleanup.py
    utils/
      paths.py
      urls.py
      files.py
      subprocess.py
    main.py
  config/
    beets/
      config.yaml
  requirements.txt
  .env.example
  README.md
```

## 27. MVP

В MVP входят:

1. запуск без Docker;
2. systemd service;
3. авторизация по Telegram ID;
4. ReplyKeyboard-интерфейс;
5. загрузка аудиофайлов;
6. скачивание по разрешённой ссылке;
7. allowlist/blocklist доменов;
8. сохранение в `/srv/music/incoming`;
9. импорт через beets;
10. очередь задач;
11. просмотр статуса;
12. очистка tmp;
13. базовые логи;
14. SQLite база;
15. интеграция с Navidrome через файловую библиотеку.

## 28. Версия 2

Во вторую версию можно добавить:

1. прогресс скачивания;
2. выбор качества;
3. FLAC/MP3 режимы;
4. поиск по локальной библиотеке;
5. удаление треков;
6. проверку дублей;
7. импорт плейлистов как wanted-list;
8. кнопку “открыть в Navidrome”;
9. Web UI;
10. интеграцию с MusicBrainz API;
11. отдельный worker-процесс;
12. уведомление после скана Navidrome.

## 29. Критерии готовности

Проект считается готовым, если:

1. бот запускается через systemd;
2. бот переживает перезапуск сервера;
3. Owner получает ReplyKeyboard-меню;
4. неизвестные пользователи не получают доступ;
5. можно отправить аудиофайл;
6. файл сохраняется в `/srv/music/incoming`;
7. beets импортирует файл в `/srv/music/library`;
8. Navidrome видит импортированный файл;
9. можно отправить разрешённую ссылку;
10. yt-dlp скачивает аудио;
11. очередь показывает задачи;
12. ошибки пишутся в лог;
13. tmp можно очистить через кнопку;
14. бот не использует Docker.
