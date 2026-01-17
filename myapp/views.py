from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (SignUpCredSerializer,
                          UserObjectViewSerializer)
from rest_framework.permissions import *
from .models import (UserOtp,SignUpCred,EmailOtp)
from django.core.mail import send_mail
import random
from django.db import transaction
from .tasks import sendemail,detele_phone_otp
from django.utils import timezone
import string
from .authfunctions import send_email_otp
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache
from myapp.permissions.permissions import UserPermission,OwnerOnlyPermission
from django.contrib.auth import get_user_model






class CreatePrimaryUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = SignUpCredSerializer(data=request.data)
            
            if serializer.is_valid():
               serializer.save(status="Pending")
               return Response({
                    'user': serializer.data,
                    'message': 'User created successfully'
                }, status=status.HTTP_201_CREATED)
                    
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class resendPhoneOtp(APIView):
    def post(self,request):
        phone = request.data.get('phone')
        

        if phone is None:
            return Response(
                {
                    'message' : 'phone number is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )   
        

        try:
            with transaction.atomic():
                user = SignUpCred.objects.select_for_update().get(phone_number = phone)
                otp_record = UserOtp.objects.select_for_update().get(user=user)
        except SignUpCred.DoesNotExist:
            return Response(
                {
                    'message' : 'User with this phone number does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )  
        except UserOtp.DoesNotExist:
            return Response(
                {
                    'message' : 'OTP record for this user does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )          


        if not otp_record.can_resend():
            return Response({
                'message' : f'please wait for {otp_record.resend_timeout()} seconds to resend otp'
            },status=status.HTTP_400_BAD_REQUEST
            )
        
        otp = ''.join(random.choices(string.digits,k=6))
        otp_record.PhoneOtp = otp
        otp_record.created_at = timezone.now()
        otp_record.save()
        sendemail.delay(phone,otp)
        detele_phone_otp.apply_async((user.id,),countdown=300)
        return Response(
            {
                'message' : 'OTP resent successfully'
            },
            status=status.HTTP_200_OK
        )

        
        
 


        
   
        



class PhoneOtpVarification(APIView):
    def post(self,request):
        phone = request.data.get('phone')        
        otp = request.data.get('otp')
        self.is_true = False

        if phone is None or otp is None:
            return Response({
                'message' : 'phone or otp is required'
            })
        
        try:
            user = SignUpCred.objects.get(phone_number = phone)
            print('ans',user.id)
            if user:
                result = UserOtp.objects.get(user=user)
                print(result.user.fullName)
                if result.PhoneOtp == otp:
                    result.PhoneOtp = "true"
                    result.save()
                    return Response(
                        {
                            "message" : "OTP matched successfully and Email otp will be send to you email in 5 minutes"
                        },
                        status=status.HTTP_202_ACCEPTED
                    )
                   
                else:
                    return Response({
                        'message' : 'OTP did not match'
                    },status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({
                "message" : str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        






class Send_otp_Email(APIView):
    def post(self,request):
        email = request.data.get('email')

        try:
            with transaction.atomic():
                user = SignUpCred.objects.select_for_update().get(email=email)
                phone_otp_record = UserOtp.objects.select_for_update().get(user=user)

                if phone_otp_record.PhoneOtp != "true":
                    return Response({
                        'message' : 'Phone number is not verified yet'
                    },status=status.HTTP_400_BAD_REQUEST)
                
                
                otp = ''.join(random.choices(string.digits,k=6))
                email_otp_record,created = EmailOtp.objects.select_for_update().get_or_create(user=user,
                                                                                              defaults={
                                                                                                  'EmialOtp' : otp
                                                                                              })
                if created:
                    send_email_otp(email=user.email,otp=otp)
                    return Response({
                        'message' : 'Email OTP sent successfully'
                    },status=status.HTTP_201_CREATED
                    )
                
                if not email_otp_record.Email_otp_NotExpired():
                    return Response({
                        'message' : f'please wait for {email_otp_record.remaining_time()} seconds to resend otp'
                    },status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                
                
                otp = ''.join(random.choices(string.digits,k=6))
                email_otp_record.EmialOtp = otp
                email_otp_record.created_at = timezone.now()
                email_otp_record.save()
                send_mail(
                    subject="Email otp verification",
                    message=f'Your Email OTP is {otp}',
                    from_email="www.BRD Driver hire.com",
                    recipient_list=[user.email]
                )
                return Response({
                    'message' : 'Email OTP resent successfully'
                },status=status.HTTP_200_OK)
                
            
        except SignUpCred.DoesNotExist:
            return Response({
                'message' : 'User with this email does not exist'
            },status=status.HTTP_404_NOT_FOUND)
        
        except UserOtp.DoesNotExist:
            return Response({
                'message' : 'OTP record for this user does not exist'
            },status=status.HTTP_404_NOT_FOUND)
        

     
        
        
        
        
                
        

         

class EmailVarification(APIView):
    def post(self,request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email and not otp:
            return Response({
                "message":"email or otp is required"
            })
        
        try:
             with transaction.atomic():
                 user = SignUpCred.objects.select_for_update().get(email=email)
                 email_otp_record = EmailOtp.objects.select_for_update().get(user=user)
                 if email_otp_record.EmialOtp == otp:
                     email_otp_record.user.status = "approved"
                     email_otp_record.user.save()
                     data = {
                         "fullName" : email_otp_record.user.fullName,
                         "email" : email_otp_record.user.email,
                         "phone" : email_otp_record.user.phone_number,
                         "password" : email_otp_record.user.pasword
                     }

                     channel_layer = get_channel_layer()
                     async_to_sync(channel_layer.group_send)(
                         f"user_{email_otp_record.user.id}",{
                             'type' : "email.verification",
                             "data" : data
                         }
                     )

                     access_token = None
                     refresh_token = None

                     for _ in range(20):
                             access_token = cache.get(f'access_token_{email_otp_record.user.email}')
                             refresh_token  = cache.get(f'refresh_token_{email_otp_record.user.email}')
                             if access_token and refresh_token:
                                 break
                             import time
                             time.sleep(1)
                             
                     return Response({
                         'message' : 'Email verified successfully',
                         'access_token' : access_token,
                         'refresh_token' : refresh_token
                     },status=status.HTTP_200_OK)
                 
                 return Response({
                     'message' : 'Email verification failed'
                 },status=status.HTTP_400_BAD_REQUEST)

        except SignUpCred.DoesNotExist:
            return Response({
                'message' : 'User with this email does not exist'
            },status=status.HTTP_404_NOT_FOUND)
        except EmailOtp.DoesNotExist:
            return Response({
                'message' : 'OTP record for this user does not exist'
            },status=status.HTTP_404_NOT_FOUND)

        except EmailOtp.DoesNotExist:
            return Response({
                'message' : 'OTP record for this user does not exist'
            },status=status.HTTP_404_NOT_FOUND)



class ProfileViewApi(APIView):
    permission_classes = [IsAuthenticated, UserPermission, OwnerOnlyPermission]

    def get(self, request):
        serializer = UserObjectViewSerializer(request.user)
        return Response(
            {"user": serializer.data},
            status=status.HTTP_200_OK
        )
