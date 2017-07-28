from __future__ import absolute_import, unicode_literals
import django
import os
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mystory.settings')
django.setup()
from celery import Celery
from .tasks import pollSession

app = Celery('mystory')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, pollSession.s(), name='Check for the end of a session')