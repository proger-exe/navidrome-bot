from __future__ import annotations

from urllib.parse import urlparse


def normalized_host(url: str) -> str | None:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    return parsed.hostname.lower().removeprefix("www.")


def domain_matches(host: str, domain: str) -> bool:
    domain = domain.lower().removeprefix("www.")
    return host == domain or host.endswith(f".{domain}")


def is_allowed_url(url: str, allowed: list[str], blocked: list[str]) -> bool:
    host = normalized_host(url)
    if not host:
        return False
    if any(domain_matches(host, domain) for domain in blocked):
        return False
    return any(domain_matches(host, domain) for domain in allowed)
