from __future__ import annotations

from app.utils.urls import is_allowed_url, normalized_host


def test_normalized_host() -> None:
    assert normalized_host("https://www.youtube.com/watch?v=1") == "youtube.com"
    assert normalized_host("ftp://youtube.com/file") is None


def test_allowed_and_blocked_domains() -> None:
    assert is_allowed_url("https://music.youtube.com/watch", ["youtube.com"], [])
    assert is_allowed_url("https://youtu.be/abc", ["youtu.be"], [])
    assert not is_allowed_url("https://spotify.com/track/1", ["spotify.com"], ["spotify.com"])
    assert not is_allowed_url("not a url", ["youtube.com"], [])
