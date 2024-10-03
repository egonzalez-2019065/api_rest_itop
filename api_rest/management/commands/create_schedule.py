from django.core.management.base import BaseCommand
from django_q.tasks import schedule, Schedule

class Command(BaseCommand):
    help = 'Inicia la tarea programada'

    def handle(self, *args, **kwargs):
        # Verificar si la tarea ya está programada
        existing_schedule = Schedule.objects.filter(name='Insert').first()

        if existing_schedule:
            self.stdout.write(self.style.WARNING('This task already exists'))
        else:
            # Crear la tarea programada
            schedule(
                name='Insert',
                func='api_rest.tasks.task_insert_data.insert',
                minutes=1,
                repeats=-1
            )
            self.stdout.write(self.style.SUCCESS('Schedule created successfully'))
