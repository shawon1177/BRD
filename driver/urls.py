from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns= [
    path('driver-registration',views.DrivRegistration.as_view(),name="driver-registration"),
    path('driver-phone-varification',views.DriverPhoneVerification.as_view(),name='driver-phone-varification'),
    path('driver-resend-phone',views.DriverResendPhone.as_view(),name='driver-resend-phone'),
    path('driver-resend-email',views.SendEmailOTP.as_view(),name='driver-resend-email'),
    path('driver-email-varification',views.DriverEmailVarification.as_view(),name='driver-email-varification'),
    path('driver-profile',views.DriverProfileViewApi.as_view(),name='driver-profile'),
    
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )