# NavidromeBot

Telegram bot for importing uploaded audio and allowed music links into a Navidrome library through `yt-dlp` and `beets`. Deployment is direct on the host: Python venv, systemd, `/srv/music` directories, no Docker.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
```

Fill `BOT_TOKEN`, `OWNER_ID`, and optional `ALLOWED_USER_IDS` in `.env`.

## Runtime Directories

```bash
sudo mkdir -p /opt/music-bot /srv/music/incoming /srv/music/library /srv/music/tmp /srv/music/bot-data /srv/music/beets
sudo chown -R $USER:$USER /opt/music-bot /srv/music
```

## Commands

```bash
python3 -m app.main --check-config
python3 -m app.main
pytest
```

Install `deploy/music-bot.service` as `/etc/systemd/system/music-bot.service` on the server, then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now music-bot
journalctl -u music-bot -f
```

## Notes

The bot uses ReplyKeyboard menus as the primary UI. Owner settings changed through Telegram are stored in SQLite over `.env` defaults.
