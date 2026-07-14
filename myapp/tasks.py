from celery import shared_task
from django.core.mail import send_mail
from time import sleep
from .models import UserOtp,SignUpCred
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import LocationViewModel

@shared_task
def sendemail(phone,otp):
    sleep(5)
    send_mail(
        subject="Phone otp varification",
        message=f"Your OTP is {otp}",
        from_email="www.BRD Driver hire.com",
        recipient_list=[phone]
    )


@shared_task(bind=True)
def detele_phone_otp(self,user_id):
   try:
       user = SignUpCred.objects.get(id=user_id)
       with transaction.atomic():
        otp = UserOtp.objects.select_for_update().get(user=user)
        otp.PhoneOtp = ''
        otp.save()
       return f"otp for {user.fullName} is deleted successfully"

   except:
       return "somthing went wrong"



@shared_task(bind=True)
def delete_location_table():
   try:
      
     cutoff = timezone.now() - timedelta(minutes=3)
  
     cutoff_row = LocationViewModel.objects.filter(updated_at___lte=cutoff)
  
     count,_ = cutoff_row.delete()
  
     return f" deleted {count} successfully before {cutoff}"
   except Exception as e:
      return f"error occured at {e}"

