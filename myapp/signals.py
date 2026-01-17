from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (SignUpCred,UserOtp,EmailOtp)
import random
import string
import time
from django.core.mail import send_mail
from .tasks import sendemail,detele_phone_otp
from django.contrib.auth import get_user_model





@receiver(post_save,sender=SignUpCred)
def send_phone_otp(sender,instance,created,**kwargs):
    is_sent = False
    is_deletion = False
    if created:
        otp = ''.join(random.choices(string.digits,k=6))
        UserOtp.objects.create(
            user = instance,
            PhoneOtp = otp
        )
        is_sent = True
        

    if is_sent:
       sendemail.delay(instance.phone_number,otp)
       is_deletion = True

    if is_deletion:
        detele_phone_otp.apply_async((instance.id,),countdown=300)



