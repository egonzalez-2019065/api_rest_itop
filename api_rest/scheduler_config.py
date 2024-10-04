# api_rest/scheduler_config.py
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.interval import IntervalTrigger
from .tasks.task_clean_data import clear

# Configuración para los logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear y configurar el scheduler
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

def configure_scheduler():
    logger.info("Intentando agregar job 'data' al scheduler.")
    if not scheduler.get_job('data'):
        try:
            scheduler.add_job(
                clear,
                IntervalTrigger(seconds=10),
                id='data',
                max_instances=1,
                coalesce=True
            )
            logger.info("Job 'data-clear' agregado al scheduler.")
        except Exception as e:
            logger.error(f"Error al agregar el job al scheduler: {e}")
    else:
        logger.info("Job 'data-clear' ya fue agregado al scheduler.")

try:
    scheduler.start()
    logger.info("Scheduler iniciado.")
except Exception as e:
    logger.error(f"Error al iniciar el scheduler: {e}")
    