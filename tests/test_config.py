from __future__ import annotations

from app.core.config import Settings


def test_settings_parse_csv_and_ids() -> None:
    settings = Settings(
        BOT_TOKEN="token",
        OWNER_ID="10",
        ALLOWED_USER_IDS="20, 30",
        YTDLP_ALLOWED_DOMAINS="youtube.com, youtu.be",
    )

    assert settings.owner_id == 10
    assert settings.allowed_user_ids == [20, 30]
    assert settings.ytdlp_allowed_domains == ["youtube.com", "youtu.be"]


def test_settings_parse_csv_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("ALLOWED_USER_IDS", "20,30")
    monkeypatch.setenv("YTDLP_ALLOWED_DOMAINS", "youtube.com,youtu.be")
    monkeypatch.setenv("YTDLP_BLOCKED_DOMAINS", "spotify.com,deezer.com")

    settings = Settings(BOT_TOKEN="token", OWNER_ID="10")

    assert settings.allowed_user_ids == [20, 30]
    assert settings.ytdlp_allowed_domains == ["youtube.com", "youtu.be"]
    assert settings.ytdlp_blocked_domains == ["spotify.com", "deezer.com"]
