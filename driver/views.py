from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from driver.serializers import DriverModelSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from myapp.tasks import sendemail
import random
import string
from .models import DriverOtp,DriverEmail
from django.db.transaction import atomic
from rest_framework.parsers import MultiPartParser, FormParser
from .models import DriverEmail,DriverModel,DriverOtp,DriverProfile
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.utils import timezone
from myapp.serializers import UserObjectViewSerializer
from django.contrib.auth import get_user_model
from driver.serializers import DriverProfileSerializer
from driver.permissions import OnlyAdminAndOwner





class DrivRegistration(APIView):
     parser_classes = (MultiPartParser, FormParser)
     def post(self,request):
          serialiser = DriverModelSerializer(
               data=request.data
          )
          if serialiser.is_valid():
               user = serialiser.save()

               image = request.build_absolute_uri(user.DL_frontside.url) if user.DL_frontside else None
               image = image.replace("http://","https://")
               
               return Response(
                    {
                         'message' : 'register registered successfully otp sent to you phone number',
                         'serializer' : serialiser.data
                    },
                    status=status.HTTP_201_CREATED
               )
               
          return Response(
               serialiser.errors,
               status=status.HTTP_400_BAD_REQUEST
          )





class DriverPhoneVerification(APIView):
     def post(self,request):
         phone = request.data.get('phone')
         otp = request.data.get('otp')

         if not phone and otp:
             return Response(
                 {
                     'message' : 'otp or phone number is required'
                 },status=status.HTTP_404_NOT_FOUND
             )
         
         
         try:
             with atomic():
               user = DriverModel.objects.select_for_update().get(phone_number=phone)
               phone_num = DriverOtp.objects.select_for_update().get(user=user)


         
         except DriverModel.DoesNotExist:
             return Response({
                 'message' : 'User with this phone number does not exist'
             },status=status.HTTP_404_NOT_FOUND)
         
         
         except DriverOtp.DoesNotExist():
             return Response({
                 'message' : 'does not exist DriverOtp field'
             },status=status.HTTP_404_NOT_FOUND)
         
         except Exception as e:
                   return Response({
                        'message' : str(e)
                   },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         

         if phone_num.phone_number == phone and phone_num.phone_otp == otp:
                   phone_num.is_varified = True
                   phone_num.phone_otp = ""
                   phone_num.save()
                   return Response ({
                       'message' : 'otp mached successfully'
                   },status=status.HTTP_200_OK
                   )
          
         return Response({
             'message' : "otp does not match"
         },status=status.HTTP_400_BAD_REQUEST)
             
          






class DriverResendPhone(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
         
         phone = request.data.get('phone')
         
         try:
              with atomic():
                   user = DriverModel.objects.select_for_update().get(phone_number=phone)
                   driver_otp_record,created = DriverOtp.objects.select_for_update().get_or_create(
                        user=user,
                        defaults={
                             'phone_number' : phone,
                             'phone_otp' : ''.join(random.choices(string.digits,k=6))
                        }
                   )

                   if created:
                        sendemail(
                             phone,
                             driver_otp_record.phone_otp
                        )
                        
                        return Response(
                             {
                                  'message' : f'{driver_otp_record.phone_otp} send to {phone}'
                             },status=status.HTTP_201_CREATED
                        )
                   

                   if driver_otp_record.is_varified:
                        return Response(
                             {
                                  'message' : "email is already verified"
                             },status=status.HTTP_400_BAD_REQUEST
                        )

                   if not driver_otp_record.can_resend():
                        return Response(
                             {
                                  'message' : f'resend otp after {driver_otp_record.resed_timeout()} seconds'
                             },status=status.HTTP_429_TOO_MANY_REQUESTS
                        )
                   
                   otp = ''.join(random.choices(string.digits,k=6))
                   driver_otp_record.phone_otp = otp
                   driver_otp_record.created_at = timezone.now()
                   driver_otp_record.is_varified = False
                   driver_otp_record.save()
                   return Response(
                        {
                             'message' : f'{otp} send to {driver_otp_record.phone_number}'
                        },status=status.HTTP_201_CREATED
                   )

         except DriverModel.DoesNotExist:
              return Response(
                   {
                        'message' : 'user with this phone number does not exit'
                   },status=status.HTTP_404_NOT_FOUND
              )
         
         except Exception as e:
           return Response(
                {
                     'message' : str(e)
                }
           )






class SendEmailOTP(APIView):
     def post(self,request):
          email = request.data.get('email')

          is_sent = False

          if not email:
               return Response(
                    {
                         'message' : "email field is required"
                    },status=status.HTTP_400_BAD_REQUEST
               )

          try:

             with atomic():  
               user = DriverModel.objects.select_for_update().get(email=email)
               driver_eamil_otp_record,created = DriverEmail.objects.select_for_update().get_or_create(
                    user=user,
                    defaults={
                         'email' : email,
                         'EmialOtp' : ''.join(random.choices(string.digits,k=6))
                    }
               )

               if created:
                    sendemail(
                         driver_eamil_otp_record.email,
                         driver_eamil_otp_record.EmialOtp
                    )
                    return Response(
                         {
                              'meaage' : f"{driver_eamil_otp_record.EmialOtp} is sent to {driver_eamil_otp_record.email}"
                         },status=status.HTTP_201_CREATED
                    )
               
               if not driver_eamil_otp_record.can_resend():
                    return Response(
                         {
                              'message' : f"resend otp to after {driver_eamil_otp_record.resend_timeout()}"
                         },status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
               
               otp = ''.join(random.choices(string.digits,k=6))
               driver_eamil_otp_record.EmialOtp = otp
               driver_eamil_otp_record.created_at = timezone.now()
               driver_eamil_otp_record.is_varified = False
               driver_eamil_otp_record.save()

               is_sent = True

               if is_sent:
                    sendemail(
                         driver_eamil_otp_record.email,
                         otp
                    )
                    return Response(
                         {
                              'meaage' : f"{driver_eamil_otp_record.EmialOtp} is sent to {driver_eamil_otp_record.email}"
                         },status=status.HTTP_201_CREATED
                    )     
               
          
          
          except DriverModel.DoesNotExist:
               return Response(
                    {
                         'message' : "email with this email does not exit"
                    },status=status.HTTP_404_NOT_FOUND
               )
          
          except Exception as e:
               return Response(
                    {
                         'message' : str(e)
                    },status=status.HTTP_500_INTERNAL_SERVER_ERROR
               )






class DriverEmailVarification(APIView):
     permission_classes = [AllowAny]

     def post(self,request):
          email = request.data.get('email')
          otp = request.data.get('otp')


          if not otp :
               return Response(
                    {
                         'message':"otp field is required"
                    },status=status.HTTP_400_BAD_REQUEST
               )
          
          try:
               with atomic():
                    user = DriverModel.objects.select_for_update().get(email=email)
                    phone_otp_record = DriverOtp.objects.select_for_update().get(user=user)
                    driver_email_otp_record = DriverEmail.objects.select_for_update().get(user=user)

                    if not phone_otp_record.is_varified:
                         return Response(
                              {
                                   'message' : "first verify you phone number"
                              },status=status.HTTP_400_BAD_REQUEST
                         )
               

                   
                    if driver_email_otp_record.attemps > 3:
                         return Response(
                              {
                                   'message' : "you have passed the limit"
                              },status=status.HTTP_502_BAD_GATEWAY
                         )
                    
                    if driver_email_otp_record.EmialOtp != otp:
                         driver_email_otp_record.attemps +=1
                         driver_email_otp_record.save()
                         return Response(
                              {
                                   'message' : "otp did not match"
                              },status=status.HTTP_400_BAD_REQUEST
                         )
                    driver_email_otp_record.EmialOtp = ""
                    driver_email_otp_record.is_varified = True
                    driver_email_otp_record.save()

                    user = driver_email_otp_record.user
                    user.is_varified = True
                    user.save()
                   
                    
                    return Response(
                         {
                              'message' : "otp matched successfully you will be reported in 24 hours"
                         },status=status.HTTP_200_OK
                    )


                   
                    
          except DriverModel.DoesNotExist:
               return Response(
                    {
                         'message' : "user with this email is not found"
                    },status=status.HTTP_404_NOT_FOUND
               )
          
          except DriverEmail.DoesNotExist:
               return Response(
                    {
                         'message' : "email not found"
                    },status=status.HTTP_404_NOT_FOUND
               )
          
          except Exception as e:
               return Response(
                    {
                         'message' : str(e)
                    },status=status.HTTP_500_INTERNAL_SERVER_ERROR
               )




class DriverProfileViewApi(APIView):
     permission_classes = [IsAuthenticated,OnlyAdminAndOwner]

     def get(self,request):
          UserModel = get_user_model()


          user = UserModel.objects.get(id = request.user.id)
          profile = DriverProfile.objects.get(user=user)
          serializer = DriverProfileSerializer(profile)


          return Response(
               {
                    'profile' : serializer.data
               },status=status.HTTP_200_OK
          )