from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DriverModel,DriverOtp
from django.core.mail import send_mail
import random
import string
from myapp.tasks import sendemail



@receiver(post_save, sender=DriverModel)
def send_phone_otp(sender, instance, created, **kwargs):
    if created:
        otp = ''.join(random.choices(string.digits, k=6))

        DriverOtp.objects.get_or_create(
            user=instance,
            defaults={
                "phone_number": instance.phone_number,
                "phone_otp": otp
            }
        )

        sendemail(instance.phone_number, otp)

