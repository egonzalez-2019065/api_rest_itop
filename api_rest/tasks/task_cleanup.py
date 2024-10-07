
import logging
from django_apscheduler.models import DjangoJobExecution

# Configuración para los logs
logger = logging.getLogger(__name__)

def cleanup_records():
    # Obtiene todos los registros de DjangoJobExecution
    records = DjangoJobExecution.objects.all()
    if records.exists():
        # Elimina todos los registros si existen
        records.delete()    
        logger.info("Se eliminaron todos los registros creados por la ejecución de tareas en segundo plano.")
    else:
        logger.info("No se han generado registros por tareas en segundo plano ejecutadas.")
