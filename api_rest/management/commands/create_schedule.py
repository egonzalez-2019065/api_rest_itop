from django.core.management.base import BaseCommand
from api_rest.scheduler_config import configure_scheduler

class Command(BaseCommand):
    help = 'Inicia la tarea programada'

    def handle(self, *args, **kwargs):
        # Verificar si la tarea ya está programada
        try:
            configure_scheduler()
        except Exception as e: 
            print(f"Error intentando crear las tareas {e}")