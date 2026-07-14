"""Leaderboard update tasks."""

import logging
from app.workers.celery_app import app

logger = logging.getLogger("rideverse.workers.leaderboard")


@app.task
def update_player_score(player_id: str, category: str, score: int) -> dict:
    """Update a player's score in a leaderboard category.

    Args:
        player_id: Player to update.
        category: Leaderboard category (e.g. racing, combat, wealth).
        score: New score value.

    Returns:
        dict with update status and rank.
    """
    logger.info("update_score player=%s category=%s score=%d", player_id, category, score)
    # TODO: Update sorted set in Redis
    return {"status": "updated", "player_id": player_id, "category": category, "rank": 0}


@app.task
def refresh_leaderboard(category: str) -> dict:
    """Recalculate and cache a full leaderboard."""
    logger.info("refresh_leaderboard category=%s", category)
    # TODO: Rebuild leaderboard cache
    return {"status": "refreshed", "category": category}


@app.task
def refresh_all_leaderboards() -> dict:
    """Refresh all leaderboard categories."""
    categories = ["racing", "combat", "wealth", "missions", "reputation"]
    for category in categories:
        refresh_leaderboard.delay(category)
    return {"status": "queued", "categories": categories}


@app.task
def get_leaderboard(category: str, limit: int = 50, offset: int = 0) -> list[dict]:
    """Retrieve a leaderboard page.

    Args:
        category: Leaderboard category.
        limit: Number of entries to return.
        offset: Pagination offset.

    Returns:
        List of leaderboard entries.
    """
    logger.info("get_leaderboard category=%s limit=%d offset=%d", category, limit, offset)
    # TODO: Read from Redis sorted set
    return []


@app.task
def reset_weekly_leaderboards() -> dict:
    """Reset weekly leaderboard scores."""
    logger.info("resetting_weekly_leaderboards")
    # TODO: Archive current scores and reset
    return {"status": "reset"}


@app.task
def reset_monthly_leaderboards() -> dict:
    """Reset monthly leaderboard scores."""
    logger.info("resetting_monthly_leaderboards")
    # TODO: Archive current scores and reset
    return {"status": "reset"}
