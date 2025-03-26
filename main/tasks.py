import threading
import time
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
from .models import PendingUser


def cleanup_pending_users():
    """Функция для удаления неактивных пользователей."""
    while True:
        # Динамически загружаем модель PendingUser
        pendingUser = apps.get_model('main', 'PendingUser')

        expiration_time = timezone.now() - timedelta(minutes=60)
        pendingUser.objects.filter(created_at__lt=expiration_time).delete()
        print("Удалены устаревшие записи из PendingUser.")

        # Засыпаем на 30 минут
        time.sleep(60 * 60)