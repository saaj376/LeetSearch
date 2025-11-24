
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from models import (
    CollegeSearchResponse,
    CollegeUserResult,
    HealthResponse,
    Profile,
    ProfileResponse,
    RefreshRequest,
    RefreshResponse,
)
from scraper import fetch_user_profile, scrape_contest_usernames

logger = logging.getLogger("leetsearch")
logging.basicConfig(level=logging.INFO)

APP_ROOT = Path(__file__).parent
DB_PATH = APP_ROOT / "users.json"

app = FastAPI(
    title="LeetSearch Backend",
    version="1.0.0",
    description="API surface that powers the LeetSearch Chrome extension.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _read_database() -> Dict[str, dict]:
    """Safely load the cached user database."""
    try:
        with DB_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        logger.warning("users.json not found — returning empty cache.")
        return {}
    except json.JSONDecodeError as exc:
        logger.error("users.json is corrupted: %s", exc)
        return {}


def _write_database(db: Dict[str, dict]) -> None:
    """Persist the cache atomically."""
    tmp_path = DB_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(db, handle, indent=2, ensure_ascii=False)
    tmp_path.replace(DB_PATH)
    logger.info("Saved %s cached profiles.", len(db))


def _last_updated() -> datetime | None:
    """Return the mtime of users.json as an aware datetime if it exists."""
    if not DB_PATH.exists():
        return None
    ts = DB_PATH.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _search_by_college(query: str) -> List[CollegeUserResult]:
    db = _read_database()
    needle = query.strip().lower()
    matches: List[CollegeUserResult] = []

    for username, profile in db.items():
        if not profile:
            continue

        school = (profile.get("school") or "").strip()
        if not school:
            continue

        if needle in school.lower():
            matches.append(
                CollegeUserResult(
                    username=username,
                    realName=profile.get("realName"),
                    school=school,
                    ranking=profile.get("ranking"),
                    country=profile.get("countryName"),
                )
            )

    return matches

def run_refresh_cycle(pages: int, max_users: int) -> None:
    """
    Scrape contest pages and update the cache.

    Heavy network work happens here so the API endpoint can respond quickly.
    """
    logger.info("Starting refresh cycle pages=%s max_users=%s", pages, max_users)
    start = time.perf_counter()
    db = _read_database()
    usernames = scrape_contest_usernames(pages=pages)
    usernames = usernames[:max_users]

    updated = 0
    for username in usernames:
        profile = fetch_user_profile(username)
        if not profile:
            continue
        db[username] = profile
        updated += 1

    if updated:
        _write_database(db)

    logger.info(
        "Refresh cycle complete: %s updated profiles in %.2fs",
        updated,
        time.perf_counter() - start,
    )

@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    """Simple readiness probe."""
    db = _read_database()
    return HealthResponse(
        profiles_cached=len(db),
        last_updated=_last_updated(),
    )


@app.get(
    "/search/college",
    response_model=CollegeSearchResponse,
    tags=["search"],
)
async def search_college(query: str = Query(..., min_length=2, description="College substring to match.")) -> CollegeSearchResponse:
    """Return cached profiles whose school matches the provided query."""
    matches = _search_by_college(query)
    return CollegeSearchResponse(query=query, total=len(matches), results=matches)


@app.get("/profiles/{username}", response_model=ProfileResponse, tags=["profiles"])
async def get_profile(username: str, refresh: bool = Query(False, description="Fetch from LeetCode even if a cached record exists.")) -> ProfileResponse:
    """
    Return the cached profile for a username.

    If `refresh=true`, we hit the live scraper and update the cache.
    """
    db = _read_database()
    cached_profile = db.get(username)

    if cached_profile and not refresh:
        return ProfileResponse(cached=True, profile=Profile(**cached_profile))

    live_profile = fetch_user_profile(username)
    if not live_profile:
        if cached_profile:
            # Could not refresh; fall back to stale data.
            return ProfileResponse(cached=True, profile=Profile(**cached_profile))
        raise HTTPException(status_code=404, detail="Profile not found on LeetCode.")

    db[username] = live_profile
    _write_database(db)
    return ProfileResponse(cached=False, profile=Profile(**live_profile))


@app.post("/refresh", response_model=RefreshResponse, tags=["admin"])
async def refresh(
    request: RefreshRequest,
    background_tasks: BackgroundTasks,
) -> RefreshResponse:
    """Kick off a background refresh cycle."""
    background_tasks.add_task(run_refresh_cycle, request.pages, request.max_users)
    return RefreshResponse(
        started=True,
        pages=request.pages,
        max_users=request.max_users,
        message="Refresh cycle scheduled.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

