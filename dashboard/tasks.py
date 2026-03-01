from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_notification(self,email,subject,message):
    send_mail(
        subject=subject,
        message=message,
        from_email='your_email@example.com',
        recipient_list=[email],
        fail_silently=False,
    )