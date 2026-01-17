from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from driver.serializers import DriverModelSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



def send_to_consumers(data):
    user_id = data.get('user_id')
    FullName = data.get('FullName')
    email = data.get("describtions")
    phone_number = data.get('phone_number')
    status = data.get('status')
    DL_frontside = data.get('DL_frontside')
    DL_Backside = data.get('DL_Backside')
    NID_frontside = data.get('NID_frontside')
    NID_backside = data.get('NID_backside')
    CV_field = data.get('CV_field')

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
      f'user_{user_id}',{
          'type' : 'create.driver',
          'data' : {
              'FullName' : FullName,
              'email' : email,
              'phone_number' : phone_number,
              'status' : status,
              'DL_frontside' : DL_frontside,
              'DL_Backend' : DL_Backside,
              'NID_frontside' : NID_frontside,
              'NID_backside' : NID_backside,
              'CV_field' : CV_field
          }
      }
    ) 




class DrivRegistration(APIView):
    def post(self,request):
        try:
            
          serializer = DriverModelSerializer(data=request.data)
          if serializer.is_valid():
              serializer.status = "pending"
              serializer.save()
              data = {
                'FullName' : serializer.data.FullName,
                'email' : serializer.data.email,
                'phone_number' : serializer.data.describtions,
                'status' : serializer.data.status,
                'DL_frontside' : serializer.data.Dl_frontside,
                'DL_Backend' : serializer.data.DL_Backside,
                'NID_frontside' : serializer.data.NID_frontside,
                'NID_backside' : serializer.data.NID_backside,
                'CV_field' : serializer.data.CV_field
            }
  
              send_to_consumers(data)
              return Response({
                      'message' : 'data sent to consumer'
                  },status=status.HTTP_201_CREATED)
          return Response({
              'message' : 'failed to create drive user'
          },status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                'message' : "something went wrong"
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR
            
            )  
              
            




