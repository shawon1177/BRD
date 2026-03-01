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
 
]