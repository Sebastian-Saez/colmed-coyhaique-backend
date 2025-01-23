from celery import shared_task
from base_colmed.management.commands.import_medicos import Command
from datetime import datetime

@shared_task(name='importar_medicos_diariamente')
def importar_medicos_diariamente():
    """
    Ejecuta la importación de médicos como una tarea asíncrona de Celery.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Ejecutando tarea Celery: importación de médicos.")

    command = Command()
    command.handle()  

    print(f"[{now}] Importación de médicos finalizada.")
