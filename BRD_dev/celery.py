import os
from celery import Celery
from time import sleep
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BRD_dev.settings')
app = Celery('BRD_dev')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()



app.conf.beat_schedule = {
    'update_attems_every_2_minute' : {
        'task' : "driver.tasks.update_attemps",
        'schedule' : crontab(minute='*/2')

    }
}