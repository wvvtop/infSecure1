from threading import Thread
import time
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        """Запускаем фоновые задачи при старте Django."""
        # Импортируем функции только внутри метода ready
        from .tasks import cleanup_pending_users, cleanup_expired_codes

        # Запускаем задачи в отдельных потоках
        pending_users_thread = Thread(target=cleanup_pending_users, daemon=True)
        pending_users_thread.start()

        reset_codes_thread = Thread(target=cleanup_expired_codes, daemon=True)
        reset_codes_thread.start()
