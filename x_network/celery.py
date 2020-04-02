from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'x_network.settings')

app = Celery('x_network')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.自动发现别的app里的tasks
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.CELERY_TIMEZONE = 'Asia/Shanghai'
platforms.C_FORCE_ROOT = True