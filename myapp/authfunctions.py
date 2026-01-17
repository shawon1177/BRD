from django.core.mail import send_mail
from time import sleep


def send_email_otp(**kwargs):
    email = kwargs.get('email')
    otp = kwargs.get('otp')
    sleep(10)
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}',
        'from@example.com',
        [email],
        fail_silently=False,
    )