from django.urls import path
from . import views

urlpatterns = [
    path('register',views.CreatePrimaryUser.as_view(),name='register'),
    path('mobile-varification',views.PhoneOtpVarification.as_view(),name='mobile'),
    path('resend-phone-otp',views.resendPhoneOtp.as_view(),name="resend-phone"),
    path('resend-email-otp',views.Send_otp_Email.as_view(),name="resend-email"),
    path('email-verification',views.EmailVarification.as_view(),name="email-verification"),
    path('profileview',views.ProfileViewApi.as_view(),name="profileview"),
]
