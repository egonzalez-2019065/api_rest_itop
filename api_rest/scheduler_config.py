# api_rest/scheduler_config.py
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from .tasks.task_clean_data import clear

# Configuración para los logs
logger = logging.getLogger(__name__)


def configure_scheduler():
    # Crear y configurar el scheduler
    scheduler = BlockingScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    logger.info("Intentando agregar job 'data' al scheduler.")

    if not scheduler.get_job('data'):
        try:
            scheduler.add_job(
                clear,
                CronTrigger(second=10),
                id='data',
                max_instances=1,
                coalesce=True
            )
            logger.info("Job 'data' agregado al scheduler.")
        except Exception as e:
            logger.error(f"Error al agregar el job al scheduler: {e}")
    else:
        logger.info("Job 'data' ya fue agregado al scheduler.")

    try:
        scheduler.start()
    except Exception as e:
        logger.error(f"Error al iniciar el scheduler: {e}")
