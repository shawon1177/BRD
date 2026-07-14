from django.urls import path
from . import views

urlpatterns = [
    path('register',views.CreatePrimaryUser.as_view(),name='register'),
    path('mobile-varification',views.PhoneOtpVarification.as_view(),name='mobile'),
    path('resend-phone-otp',views.resendPhoneOtp.as_view(),name="resend-phone"),
    path('resend-email-otp',views.Send_otp_Email.as_view(),name="resend-email"),
    path('email-verification',views.EmailVarification.as_view(),name="email-verification"),
    path('profileview',views.ProfileViewApi.as_view(),name="profileview"),
    path('forgetpassword',views.ForgetUserPasswordApi.as_view(),name='forgetpassword'),
    path('userotpvarification',views.UserotpVarificationAPI.as_view(),name='userotpvarification'),
    path('userpasswordreset',views.ResetpasswordAPIView.as_view(),name='userpasswordreset'),
    path('getuserinfo/<str:email_or_phone>/', views.GetUserInfo.as_view()),
    path('LoginUserView',views.LoginAPIView.as_view(),name='LoginUserView'),
    path('makeorder',views.MakeOrderApi.as_view(),name="makeorder"),
    path('get-orders',views.OrderDropApiView.as_view(),name="get-orders"),
    path('upload-profile-picture', views.UploadProfilePictureAPIView.as_view(), name='upload-profile-picture'),
    path('update-profile', views.UpdateProfileApiView.as_view(), name='update-profile'),

]
