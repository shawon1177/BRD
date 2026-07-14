from django.shortcuts import render
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import AdminApprovedUser,OnlyAdminAndOwner
from myapp.serializers import UserObjectViewSerializer
from driver.serializers import DriverModelSerializer,DriverProfileSerializer
from driver.models import DriverModel,DriverEmail,DriverOtp,DriverProfile
from django.contrib.auth import get_user_model
from django.db import transaction
from myapp.models import MakeOrderModel
from myapp.serializers import MakeOrderSerializer
from rapidfuzz import fuzz,process
from .permissions import AdminApprovedUser
from .serializers import (DriverProfileViewSerializer,
                          UserViewSerializer,
                          CarUserViewSerializer,
                          DriverConfirmationSerializer,
                          HireConfirmationSerializer,
                          DriverBookingSerializer
                          )
from .models import DriverConfirmationModel,HireConfirmationModel,DriverBookingModel
from django.db.transaction import atomic
from .tasks import send_email_notification







class GetDriverList(APIView):
    permission_classes = [AdminApprovedUser]

    def get(self,requst):
        driver_list = []
        drivers = DriverModel.objects.all()

        for driver in drivers:
            phone_otp_record_varified = DriverOtp.objects.filter(user=driver,is_varified=True).exists()
            email_otp_record_varified = DriverEmail.objects.filter(user=driver,is_varified=True).exists()


            if phone_otp_record_varified and email_otp_record_varified:
                driver_list.append(driver)
        

        if driver_list:
           serializer = DriverModelSerializer(driver_list,many=True)
           return Response(
                {
                    'Drivers' : serializer.data
                },status=status.HTTP_200_OK
            )
        return Response(
            {
                'Drivers' : []
            },status=status.HTTP_409_CONFLICT
        )  
        
          
        
       


class DriverRegistrationApproved(APIView):
    permission_classes = [AdminApprovedUser]

    def post(self,reuquest):
        id = reuquest.data.get('id')
        UserModel = get_user_model() 

        try:
            driver = DriverModel.objects.get(id=id)
        except DriverModel.DoesNotExist:
            return Response(
                {
                    'message' : "driver does not exist"
                },status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'message' : str(e)
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR

            )
        

        with transaction.atomic(using='default'):
            user,_ = UserModel.objects.using('default').get_or_create(
                email = driver.email,
                defaults={
                    'fullName' : driver.FullName,
                    'phone' : driver.phone_number,
                    'is_active' : True,
                    'is_driver' : True,
                }
                )

            user.set_password(driver.password)
            user.save(using='default')
            send_email_notification.delay(user.email, "Driver Registration Approved", "Your driver registration has been approved you can login now.")

            driver_profile,created  = DriverProfile.objects.using('default').get_or_create(
                user=user,
                defaults={
                    'DL_frontside': driver.DL_frontside,
                    'DL_Backside': driver.DL_Backside,
                    'NID_frontside': driver.NID_frontside,
                    'NID_backside': driver.NID_backside,
                    'CV_field': driver.CV_field,
                }
                
            )

            if created:
                driver_profile.DL_frontside = driver.DL_frontside
                driver_profile.DL_Backside = driver.DL_Backside
                driver_profile.NID_frontside = driver.NID_frontside
                driver_profile.NID_backside = driver.NID_backside
                driver_profile.CV_field = driver.CV_field
                driver_profile.save(using='default')

                driver.status = "approved"
                driver.delete()
                return Response(
                    {
                        'message' : "Driver registration approved successfully"
                    },status=status.HTTP_200_OK
                )
            
            return Response(
                {
                    'message' : "Driver registration already approved"
                },status=status.HTTP_409_CONFLICT
            )    
                
            
            

      
class GetAllDriverList(APIView):
    permission_classes = [AdminApprovedUser]

    def get(self,request):
        UserModel = get_user_model()

        try:
            driver_user_list = UserModel.objects.using('default').filter(is_driver=True)
            driver_profiles = DriverProfile.objects.using('default').filter(user__in = driver_user_list)
            serializer = DriverProfileSerializer(driver_profiles,many=True)
            return Response(
                {
                    'Drivers' : serializer.data
                },status=status.HTTP_200_OK
            )   
        except Exception as e:
            return Response(
                {
                    'message' : str(e)
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        

        

        



class GetUserList(APIView):
    permission_classes = [AdminApprovedUser]

    def get(self,request):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.using('default').filter(is_driver=False)
            DriverModelSerializer = UserObjectViewSerializer(user,many=True)
            return Response(
                {
                    'users' : DriverModelSerializer.data
                },status=status.HTTP_200_OK
            )
        except:
            return Response(
                {
                    'message' : "no user available"
                },status=status.HTTP_409_CONFLICT
            )




class GetUserHireDriverList(APIView):
    permission_classes = [AdminApprovedUser]

    def get(self,request):

        requests = MakeOrderModel.objects.all()

        if requests:
            serializer = MakeOrderSerializer(requests,many=True)
            return Response(
                {
                    'requests' : serializer.data
                },status=status.HTTP_200_OK
            )
        return Response(
            {
                'message' : "no request available"
            },status=status.HTTP_409_CONFLICT
        )

        



class DriverSearch(APIView):
    permission_classes = [AdminApprovedUser]

    def get(self, request):
        query = request.data.get('query')  

        if not query:
            return Response(
                {'message': 'query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        UserModel = get_user_model()
        drivers = UserModel.objects.filter(is_driver=True).select_related('driver_profile')

        if not drivers.exists():
            return Response(
                {'message': 'no driver available'},
                status=status.HTTP_409_CONFLICT
            )

        max_matched = []

        for driver in drivers:
            scores = [
                fuzz.partial_ratio(query, driver.fullName or ""),
                fuzz.partial_ratio(query, driver.email or ""),
                fuzz.partial_ratio(query, driver.phone or ""),
            ]
            max_score = max(scores)
            if max_score >= 60:
                max_matched.append((max_score, driver))

        if not max_matched:
            return Response(
                {'message': 'no driver found'},
                status=status.HTTP_404_NOT_FOUND
            )

        max_matched.sort(key=lambda x: x[0], reverse=True)
        drivers_sorted = [item[1] for item in max_matched]

        serializer = UserViewSerializer(
            drivers_sorted,
            many=True,
            context={'request': request}
        )

        return Response(
            {'results': serializer.data},
            status=status.HTTP_200_OK
        )



               


class GetUserWithCarDetails(APIView):
    permission_classes = [AdminApprovedUser]

    def get(self,request):
        query = request.data.get('query')
        User = get_user_model()

        users = User.objects.filter(is_driver=False).select_related('customer_order')

        if not users.exists():
            return Response(
                {'message': 'no user available'},
                status=status.HTTP_409_CONFLICT
            )
        
        matched = []
        

        for user in users:
            score = [
                fuzz.partial_ratio(query,user.fullName  or ""),
                fuzz.partial_ratio(query,user.email or ""),
                fuzz.partial_ratio(query,user.phone or ""),
            ]

            max_score = max(score)
            

            if max_score >= 60:
                matched.append((max_score,user))


        if matched:
            matched.sort(key=lambda x : x[0],reverse=True)

            terms = [
                term[1] for term in matched
            ]        

            serializer = CarUserViewSerializer(
                terms,
                many=True,
                context={'request': request}
            )
            return Response(
                {
                    'results' : serializer.data
                },status=status.HTTP_200_OK
            )
        return Response(
            {
                'message' : "no user found"
            },status=status.HTTP_404_NOT_FOUND
        )








class UserDriverSession(APIView):
    def post(self,request):
        UserModel = get_user_model()
        user_id = request.data.get('user_id')
        driver_id = request.data.get('driver_id')

        with atomic():
            try:
                user = UserModel.objects.get_for_update().get(id=user_id)
                driver = UserModel.objects.get_for_update().get(id=driver_id)

                if not driver.is_driver:
                    return Response(
                        {
                            'message' : 'the user you have provided does not belong to driver list'
                        },status=status.HTTP_400_BAD_REQUEST
                    )
                if  user.is_driver:
                    return Response(
                        {
                            'message' : 'the user you have provided does not belong to user '
                        },status=status.HTTP_400_BAD_REQUEST
                    )
                
    
    
                driver_booking_record,created = DriverBookingModel.objects.get_or_create(
                    user = user,
                    driver = driver,
                    defaults = {
                        'booking_status':'pending',
                        
                    }
                )
    
                if not created:
                    return Response(
                        {
                            'message' : 'a session already exists between the user and driver',
                            'serializer': DriverBookingSerializer(driver_booking_record).data
                        },status=status.HTTP_409_CONFLICT
                    )


                send_email_notification.apply_async(
                    args = [
                        user.email,
                        'Driver Session Created',
                        'fill up the charge of 2000 Taka to confirm the session.'
                    ],
                    countdown=10
                )

                return Response(
                    {
                        'message' : 'driver session created successfully',
                        'serializer': DriverBookingSerializer(driver_booking_record).data
                    },status=status.HTTP_201_CREATED
                )

            except UserModel.DoesNotExist:
             return Response(
                {
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND
            )

            except Exception as e:
               return Response(
                   {
                       'message': 'An error occurred',
                       'error': str(e)
                   }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
               )







class AdvancePaymentConfirmationApi(APIView):
    permission_classes = [OnlyAdminAndOwner]
    def post(self,request):
        user_id = request.user.id
        user_payment = request.data.get('user_payment')
        UserModel = get_user_model()

        try:
            with atomic():
                user = UserModel.objects.get_for_update().get(id=user_id)
                user_booking_record = DriverBookingModel.objects.get_for_update().get(user=user)
                self.check_object_permissions(request, user_booking_record)
                if user_payment == 2000.00:
                  user_booking_record.booking_status = 'confirmed'
                  user_booking_record.save()

                  payment, created = DriverConfirmationModel.objects.get_for_update().get_or_create(
                      user=user,
                      driver=user_booking_record.driver,
                      defaults={
                          'confirmation_payment': user_payment,
                          'payment_confirmation': True
                          
                      }
                  )

                  if not created:
                      serializer = DriverConfirmationSerializer(payment)
                      return Response(
                          {
                              'message': 'Driver confirmation already exists',
                              'serializer': serializer.data
                          }, status=status.HTTP_409_CONFLICT
                      )
                  serializer = DriverConfirmationSerializer(payment)
                  return Response(
                      {
                          'message': 'Driver confirmation created successfully',
                          'serializer': serializer.data
                      }, status=status.HTTP_201_CREATED
                  )

        except UserModel.DoesNotExist:
            return Response(
                {
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND

            )
        except DriverBookingModel.DoesNotExist:
            return Response(
                {
                    'message': 'User booking record not found'
                }, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {
                    'message': 'An error occurred',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    
        
        



        
class GetDriverBookingViewApi(APIView):
     permission_classes = [AdminApprovedUser]

     def get(self,request):
         drivers = DriverBookingModel.objects.all()

         serializer = DriverBookingSerializer(
             drivers,
             many=True,
             context={
                 'request': request
             }

         )

         if serializer:
             return Response(
                 {
                     'drivers': serializer.data
                 },
                 status=status.HTTP_200_OK
             )

         return Response(
            {
                'drivers': []
            },status=status.HTTP_200_OK
        )
        



class ConfirmationBookingApiView(APIView):
    permission_classes = [OnlyAdminAndOwner]
    
    def get(self,request):
        paid_list = DriverConfirmationModel.objects.filter(payment_confirmation=True)

        serializer = DriverConfirmationSerializer(
            paid_list,
            many=True
        )

        if serializer:
            return Response(
                {
                    'paid_list': serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'serializer':[],
            },status=status.HTTP_200_OK
        )




class DriverFinalizeApiView(APIView):
    permission_classes = [OnlyAdminAndOwner]

    def post(self,request):
        user = request.data.get('user')
        driver = request.data.get('driver')
        UserModel = get_user_model()

        try:
            user_record = UserModel.objects.filter(user=user,driver=driver).exists()
            dirver_confirmation_record =  DriverConfirmationModel.objects.filter(user=user,driver=driver,payment_confirmation=True).exists()
        


            if user_record and dirver_confirmation_record:
                hire_driver_record,created = HireConfirmationModel.objects.get_or_create(
                    user=user,
                    driver=driver,
                    defaults={
                        'confirmation_fee' : 2000.00,
                        'is_confirm' : True,
                        'joining_month' : '01-08-2026',
                        'status' : 'accepted',
                    }
                )

                if created:
                    serializer = HireConfirmationSerializer(hire_driver_record)
                    return Response(
                        {
                            'message': 'Hire confirmation created successfully',
                            'serializer': serializer.data
                        }, status=status.HTTP_201_CREATED
                    )

                return Response(
                    {
                        'message': 'Hire confirmation already exists',
                        'serializer': serializer.data
                    }, status=status.HTTP_200_OK
                )

        except:
            pass


                
        




class ViewDriverProfile(APIView):
    permission_classes = [AdminApprovedUser]

    def get(self, request):
        id = request.query_params.get('id')

        if not id:
            return Response(
                {"error": "id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = DriverModel.objects.get(id=id)
        except DriverModel.DoesNotExist:
            return Response(
                {"error": "Driver not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DriverModelSerializer(user)
        return Response(
            {"data": serializer.data},
            status=status.HTTP_200_OK
        )