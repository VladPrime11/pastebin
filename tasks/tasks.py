from celery import shared_task
from texts.models import TextBlock
from django.utils import timezone


@shared_task
def delete_expired_links():
    expired_blocks = TextBlock.objects.filter(expires_at__lt=timezone.now())
    count = expired_blocks.count()

    expired_blocks.delete()
    return f"{count} истекших ссылок удалено."
