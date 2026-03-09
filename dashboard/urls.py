from django.urls import path
from . import views

urlpatterns = [
   path('DriverApplicants',views.GetDriverList.as_view(),name="DriverApplicants"),
   path('DriverRegistrationApproved',views.DriverRegistrationApproved.as_view(),name="DriverRegistrationApproved"),
   path('DriverViewList',views.GetAllDriverList.as_view(),name="DriverList"),
   path('UserList',views.GetUserList.as_view(),name="UserList"),
   path('RequestList',views.GetUserHireDriverList.as_view(),name="RequestList"),
   path('SearchDriver',views.DriverSearch.as_view(),name="SearchDriver"),
   path('SearchUser',views.GetUserWithCarDetails.as_view(),name="SearchUser"),
   path('User-Driver-session',views.UserDriverSession.as_view(),name='User-Driver-session'),
   path('AdvancePaymentConfirmationApi',views.AdvancePaymentConfirmationApi.as_view(),name='AdvancePaymentConfirmationApi'),
   path('GetDriverBookingViewApi',views.GetDriverBookingViewApi.as_view(),name='GetDriverBookingViewApi'),
   path('ConfirmationBookingApiView',views.ConfirmationBookingApiView.as_view(),name='ConfirmationBookingApiView'),
   path('DriverFinalizeApiView',views.DriverFinalizeApiView.as_view(),name='DriverFinalizeApiView'),
 
]