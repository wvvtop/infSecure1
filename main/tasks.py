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
        time.sleep(60 * 30)


def cleanup_expired_codes():
    """Функция для удаления устаревших кодов сброса пароля."""
    while True:
        try:
            # Динамически загружаем модель PasswordResetCode
            resetCode = apps.get_model('main', 'PasswordResetCode')

            expiration_time = timezone.now() - timedelta(minutes=10)  # 10 минут для кодов
            deleted_count = resetCode.objects.filter(created_at__lt=expiration_time).delete()[0]
            print(f"Удалено {deleted_count} устаревших кодов сброса пароля.")

        except Exception as e:
            print(f"Ошибка при очистке PasswordResetCode: {e}")

        # Засыпаем на 5 минут (можно чаще, так как коды живут всего 10 минут)
        time.sleep(60 * 5)