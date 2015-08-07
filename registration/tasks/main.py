from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(max_retries=3)
def dropbox_backup():
    from django.conf import settings
    if not settings.ENABLE_DROPBOX_BACKUP:
        return

    from dropbox_helpers import backup

    try:
        backup(logger=logger)
    except Exception, exc:
        raise self.retry(exc=exc)

if __name__ == '__main__':
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wearhacks_website.settings")
    os.environ.setdefault("APP_ENV", "dev")
    dropbox_backup()