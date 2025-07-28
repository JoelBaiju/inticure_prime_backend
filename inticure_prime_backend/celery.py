import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inticure_prime_backend.settings')

app = Celery('inticure_prime_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
