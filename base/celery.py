import os
from celery import Celery
from celery.schedules import crontab
# Define o Django settings module para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')

app = Celery('base')

# Lê configurações do Celery no settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente tasks em apps Django registrados
app.autodiscover_tasks()

# Adicionando Celery Beat
app.conf.beat_schedule = {
    "clear_expired_reservations_task": {
        "task": "tickets.tasks.clear_expired_reservations",
        "schedule": crontab(minute="*/5"),  # Executa a cada 5 minutos
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')