# Repository Guidelines

## Project Structure & Module Organization

This repository is an early-stage Python Telegram bot for importing music into Navidrome. Treat `techtask.md` as the product and architecture source of truth until implementation files exist.

Target layout:

```text
app/
  bot/handlers/      # aiogram command, message, and ReplyKeyboard flows
  bot/keyboards/     # ReplyKeyboardMarkup definitions
  bot/middlewares/   # auth and request guards
  bot/states/        # aiogram FSM states
  core/              # config and logging setup
  db/                # SQLite models, migrations/helpers, repositories
  services/          # downloader, importer, task worker, cleanup
  utils/             # path, URL, file, subprocess helpers
  main.py            # python -m app.main entrypoint
config/beets/        # beets config
tests/               # pytest tests mirroring app/ modules
```

Keep deployment assets such as `.env.example`, `requirements.txt`, README notes, and systemd examples at the repository root.

## Build, Test, and Development Commands

Use the project venv and Python 3.12+:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python -m app.main
pytest
```

Before `requirements.txt` exists, install the stack from `techtask.md`: `aiogram`, `python-dotenv`, `pydantic`, `aiofiles`, `aiosqlite`, `yt-dlp`, and `beets`.

## Coding Style & Naming Conventions

Use idiomatic Python with 4-space indentation, type hints for public functions, and small async service functions. File and module names should be `snake_case.py`; classes use `PascalCase`; constants and environment variable names use `UPPER_SNAKE_CASE`.

Do not run shell commands with `shell=True`. Use `asyncio.create_subprocess_exec` for `yt-dlp`, `beet`, and `ffmpeg`. Keep user-visible bot text in Russian unless the feature is explicitly technical.

## Testing Guidelines

Use `pytest`. Mirror source paths, for example `tests/services/test_downloader.py` for `app/services/downloader.py`. Add regression tests for URL allow/block checks, path traversal prevention, task state transitions, and access control. Prefer temp directories over real `/srv/music` paths in tests.

## Commit & Pull Request Guidelines

No Git history is present yet, so use Conventional Commits going forward: `feat: add upload handler`, `fix: block path traversal`, `test: cover task queue`. PRs should include a short behavior summary, linked issue if any, test results, and screenshots or message transcripts for Telegram UI changes.

## Security & Configuration Tips

Never commit real `.env` files, bot tokens, Telegram IDs, SQLite data, or logs. Keep examples in `.env.example`. Enforce allowed directories for file operations, normalize filenames, cap file sizes, hide internal server paths from regular users, and write full tracebacks only to logs.
