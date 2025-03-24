from threading import Thread
import time
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        """Запускаем фоновую задачу при старте Django."""
        # Импортируем функцию только внутри метода ready
        from .tasks import cleanup_pending_users

        # Запускаем задачу в отдельном потоке
        task_thread = Thread(target=cleanup_pending_users, daemon=True)
        task_thread.start()
