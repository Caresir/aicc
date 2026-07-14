"""
Metricool REST API client.
Docs: https://app.metricool.com/resources/apidocs/index.html

Required .env vars:
    METRICOOL_TOKEN   — from Account Settings → Access → API
    METRICOOL_USER_ID — numeric user ID (GET /smart/v1/users/me to find it)
    METRICOOL_BLOG_ID — numeric blog/brand ID (GET /smart/v1/users/me/blogs)
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

import httpx
from loguru import logger

_BASE = "https://app.metricool.com"

# Supported Metricool network names
NETWORKS = {
    "instagram": "instagram",
    "tiktok":    "tiktok",
    "facebook":  "facebook",
    "youtube":   "youtube",
}


def _client() -> httpx.Client:
    token = os.getenv("METRICOOL_TOKEN", "")
    if not token:
        raise ValueError("METRICOOL_TOKEN not set in .env")
    return httpx.Client(
        base_url=_BASE,
        headers={"X-Mc-Auth": token, "Content-Type": "application/json"},
        timeout=30,
    )


def _params() -> dict[str, str]:
    return {
        "userId": os.getenv("METRICOOL_USER_ID", ""),
        "blogId": os.getenv("METRICOOL_BLOG_ID", ""),
    }


# ── Account ───────────────────────────────────────────────────────────────────

def ping() -> dict[str, Any]:
    """Verify connection by fetching brand profiles."""
    with _client() as c:
        r = c.get(
            "/api/admin/simpleProfiles",
            params={"userId": os.getenv("METRICOOL_USER_ID", "")},
        )
        r.raise_for_status()
        data = r.json()
        return {
            "connected": True,
            "userId": os.getenv("METRICOOL_USER_ID"),
            "blogId": os.getenv("METRICOOL_BLOG_ID"),
            "profiles": data,
        }


# ── Scheduling ────────────────────────────────────────────────────────────────

def next_slot(tz_name: str = "America/Chicago") -> str:
    """Return the next Tuesday or Thursday at 09:00 CT as a naive ISO datetime string."""
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(tz_name)
        now = datetime.now(tz)
    except Exception:
        now = datetime.utcnow()

    for days_ahead in range(1, 8):
        candidate = now + timedelta(days=days_ahead)
        if candidate.weekday() in (1, 3):  # Tue=1, Thu=3
            slot = candidate.replace(hour=9, minute=0, second=0, microsecond=0)
            return slot.strftime("%Y-%m-%dT%H:%M:%S")

    # Fallback — shouldn't happen
    return (now + timedelta(days=2)).strftime("%Y-%m-%dT09:00:00")


def schedule_post(
    caption: str,
    media_url: str,
    networks: list[str] | None = None,
    publish_datetime: str | None = None,
    timezone: str = "America/Chicago",
) -> dict[str, Any]:
    """
    Schedule a video post in Metricool.

    Args:
        caption:          Post text / caption.
        media_url:        Publicly accessible video URL (Google Drive public link works).
        networks:         List of Metricool network names. Defaults to instagram + tiktok.
        publish_datetime: ISO 8601 datetime string (no TZ suffix), e.g. '2026-07-15T09:00:00'.
                          Defaults to next Tue/Thu 9am CT.
        timezone:         Timezone name for the publishDate. Default: America/Chicago.
    """
    if networks is None:
        networks = ["instagram", "tiktok"]

    if publish_datetime is None:
        publish_datetime = next_slot(timezone)

    # Networks must be objects: [{"network": "instagram"}, ...]
    provider_objs = [{"network": n} for n in networks]

    payload: dict[str, Any] = {
        "text": caption,
        "publicationDate": {
            "dateTime": publish_datetime,
            "timezone": timezone,
        },
        "providers": provider_objs,
        "autoPublish": True,
    }

    if media_url:
        payload["medias"] = [{"url": media_url, "type": "video"}]

    logger.info(f"[metricool] Scheduling post for {publish_datetime} on {networks}")

    with _client() as c:
        r = c.post("/api/v2/scheduler/posts", params=_params(), json=payload)
        r.raise_for_status()
        return r.json()


def schedule_carousel(
    caption: str,
    image_urls: list[str],
    publish_datetime: str | None = None,
    timezone: str = "America/Chicago",
) -> dict[str, Any]:
    """
    Schedule an Instagram carousel post (multiple images) in Metricool.

    Args:
        caption:          Post text / caption.
        image_urls:       Ordered list of 2–10 publicly accessible image URLs.
        publish_datetime: ISO 8601 datetime string, e.g. '2026-07-17T09:00:00'.
                          Defaults to next Tue/Thu 9am CT.
        timezone:         Timezone name. Default: America/Chicago.

    Instagram carousel rules enforced here:
        - Minimum 2 images, maximum 10.
        - Only Instagram supports carousels via this endpoint.
    """
    if len(image_urls) < 2:
        raise ValueError("Carousel requires at least 2 image URLs")
    if len(image_urls) > 10:
        raise ValueError("Instagram carousels support a maximum of 10 images")

    if publish_datetime is None:
        publish_datetime = next_slot(timezone)

    payload: dict[str, Any] = {
        "text": caption,
        "publicationDate": {
            "dateTime": publish_datetime,
            "timezone": timezone,
        },
        "providers": [{"network": "instagram"}],
        "autoPublish": True,
        "medias": [{"url": url, "type": "image"} for url in image_urls],
    }

    logger.info(
        f"[metricool] Scheduling carousel ({len(image_urls)} images) for {publish_datetime}"
    )

    with _client() as c:
        r = c.post("/api/v2/scheduler/posts", params=_params(), json=payload)
        r.raise_for_status()
        return r.json()


def get_scheduled_posts(from_date: str | None = None, to_date: str | None = None) -> list[dict[str, Any]]:
    """Fetch the current scheduled post queue from Metricool."""
    params = dict(_params())
    if from_date:
        params["initDate"] = from_date
    if to_date:
        params["endDate"] = to_date
    with _client() as c:
        r = c.get("/api/v2/scheduler/posts", params=params)
        r.raise_for_status()
        return r.json()


# ── Analytics ─────────────────────────────────────────────────────────────────

def get_post_analytics(
    from_date: str,
    to_date: str,
    networks: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch post-level engagement metrics from Metricool.
    Returns a list of post stat objects.

    from_date / to_date: 'YYYY-MM-DD'
    """
    params = dict(_params())
    params["initDate"] = from_date
    params["endDate"]  = to_date
    if networks:
        params["networks"] = ",".join(networks)

    with _client() as c:
        r = c.get("/api/v2/analytics/posts", params=params)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else data.get("posts", [])
