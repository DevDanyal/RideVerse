"""Celery Beat schedule configuration."""

from celery.schedules import crontab
from app.workers.celery_app import app

app.conf.beat_schedule = {
    "aggregate-daily-stats": {
        "task": "app.workers.analytics_worker.aggregate_daily_stats",
        "schedule": crontab(hour=0, minute=5),
    },
    "refresh-all-leaderboards": {
        "task": "app.workers.leaderboard_worker.refresh_all_leaderboards",
        "schedule": crontab(minute="*/15"),
    },
    "reset-weekly-leaderboards": {
        "task": "app.workers.leaderboard_worker.reset_weekly_leaderboards",
        "schedule": crontab(hour=0, minute=0, day_of_week="monday"),
    },
    "reset-monthly-leaderboards": {
        "task": "app.workers.leaderboard_worker.reset_monthly_leaderboards",
        "schedule": crontab(hour=0, minute=0, day_of_month="1"),
    },
    "cleanup-expired-sessions": {
        "task": "app.workers.notification_worker.send_notification",
        "schedule": crontab(minute="*/30"),
        "args": (),
    },
}
