

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-tokens': {
        'task': 'users.tasks.cleanup_expired_tokens_task',
        'schedule': crontab(minute=0),  # Every hour
    },
    'unlock-expired-accounts': {
        'task': 'users.tasks.unlock_expired_accounts',
        'schedule': crontab(minute=0),  # Every hour
    },
}