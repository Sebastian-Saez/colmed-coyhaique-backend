
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_colmed.settings")

app = Celery("backend_colmed")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

# Configuración de tareas programadas con Celery Beat
app.conf.beat_schedule = {
    "importar-medicos-diariamente": {
        # "task": "base_colmed.tasks.importar_medicos_diariamente",
        "task": "importar_medicos_diariamente",
        "schedule": crontab(hour=6, minute=34),
    },
}