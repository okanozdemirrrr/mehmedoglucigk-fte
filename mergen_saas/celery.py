import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mergen_saas.settings')

app = Celery('mergen_saas')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
