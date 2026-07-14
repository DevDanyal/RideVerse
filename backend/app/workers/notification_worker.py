"""Notification tasks."""

import logging
from app.workers.celery_app import app

logger = logging.getLogger("rideverse.workers.notification")


@app.task(bind=True, max_retries=3)
def send_notification(self, player_id: str, title: str, message: str, notification_type: str = "info") -> dict:
    """Send a notification to a player.

    Args:
        player_id: Target player ID.
        title: Notification title.
        message: Notification body.
        notification_type: One of info, warning, success, error.

    Returns:
        dict with delivery status.
    """
    try:
        logger.info("sending_notification player=%s type=%s", player_id, notification_type)
        # TODO: Persist to DB and push via WebSocket
        return {"status": "sent", "player_id": player_id, "type": notification_type}
    except Exception as exc:
        logger.exception("notification_failed player=%s", player_id)
        self.retry(exc=exc, countdown=30)


@app.task
def broadcast_notification(title: str, message: str, notification_type: str = "info") -> dict:
    """Broadcast a notification to all online players."""
    logger.info("broadcast_notification type=%s", notification_type)
    # TODO: Push to all connected WebSocket clients
    return {"status": "broadcast", "type": notification_type}


@app.task
def send_mission_notification(player_id: str, mission_name: str, event: str) -> dict:
    """Send a mission-related notification."""
    return send_notification.delay(
        player_id=player_id,
        title=f"Mission: {mission_name}",
        message=f"Mission event: {event}",
        notification_type="info",
    )


@app.task
def send_reward_notification(player_id: str, reward_type: str, amount: int) -> dict:
    """Send a reward notification."""
    return send_notification.delay(
        player_id=player_id,
        title="Reward Received",
        message=f"You received {amount} {reward_type}!",
        notification_type="success",
    )
