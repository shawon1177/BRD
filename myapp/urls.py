from django.urls import path
from . import views

urlpatterns = [
    path('register',views.CreatePrimaryUser.as_view(),name='register'),
    path('mobile-varification',views.PhoneOtpVarification.as_view(),name='mobile'),
    path('resend-phone-otp',views.resendPhoneOtp.as_view(),name="resend-phone"),
    path('resend-email-otp',views.Send_otp_Email.as_view(),name="resend-email"),
    path('email-verification',views.EmailVarification.as_view(),name="email-verification"),
    path('profileview',views.ProfileViewApi.as_view(),name="profileview"),
    path('forgetpassword',views.ForgetEmailPasswordApi.as_view(),name='forgetpassword'),
    path('phoneforgetpassword',views.PhoneForgetPass.as_view(),name='phoneforgetpassword'),
    path('getuserinfo',views.GetUserInfo.as_view(),name='getuserinfo'),
    path('LoginUserView',views.LoginAPIView.as_view(),name='LoginUserView'),
    path('makeorder',views.MakeOrderApi.as_view(),name="makeorder"),
    path('get-orders',views.OrderDropApiView.as_view(),name="get-orders")
    
]
