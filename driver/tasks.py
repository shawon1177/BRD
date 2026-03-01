from celery import shared_task
from .models import DriverEmail


@shared_task
def update_attemps():
    users = DriverEmail.objects.all()

    for user in users:
        if user.attemps >= 3:
            user.attemps = 0
            user.save()
        else:
            pass    

