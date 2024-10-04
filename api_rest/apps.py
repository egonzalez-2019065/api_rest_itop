from django.apps import AppConfig

class ApiRestConfig(AppConfig):
    name = 'api_rest'

    def ready(self):
        from .scheduler_config import configure_scheduler
         # Llama a la función para configurar el scheduler
        configure_scheduler()