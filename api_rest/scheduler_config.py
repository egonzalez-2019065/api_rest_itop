# api_rest/scheduler_config.py
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.models import DjangoJob
from .tasks.task_clean_data import clear
from .tasks.task_insert_data import insert

# Configuración para los logs
logger = logging.getLogger(__name__)


def configure_scheduler():
    # Crear y configurar el scheduler
    scheduler = BlockingScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    logger.info("Inicia el proceso para ejecutar los trabajos con apscheduler")


    # Elimina las tareas si existe en la BD, para evitar error de duplicidad de tareas
    if DjangoJob.objects.filter(id='data').exists():
        logger.info("El trabajo 'data' existe en la base de datos, será eliminado.")
        DjangoJob.objects.filter(id='data').delete()

    if DjangoJob.objects.filter(id='insert').exists():
        logger.info("El trabajo 'insert' existe en la base de datos, será eliminado.")
        DjangoJob.objects.filter(id='insert').delete()

    if not scheduler.get_job('data') and not scheduler.get_job('insert'):
        try:
            scheduler.add_job(
                clear,
                IntervalTrigger(seconds=10),
                id='data',
                max_instances=1,
                coalesce=True
            )

            scheduler.add_job(
                insert,
                IntervalTrigger(seconds=30),
                id='insert',
                max_instances=1,
                coalesce=True
            )

            logger.info("Tareas creadas exitosamente")
        except Exception as e:
            logger.error(f"Error al crear las tareas: {e}")
    else:
        logger.info("Los trabajos ya fueron agregados")

    try:
        scheduler.start()
    except Exception as e:
        logger.error(f"Error al iniciar el scheduler: {e}")
