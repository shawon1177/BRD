from rest_framework.serializers import ModelSerializer
from .models import SignUpCred
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()



class SignUpCredSerializer(ModelSerializer):
    
 

    class Meta:
        model = SignUpCred
        fields = ['id','fullName','email','phone_number','pasword','status']
        extra_kwargs = {
            'pasword' : {
                'write_only' : True
            },
            'status' : {
                'read_only' : True
            }
        }


    def create(self, validated_data):
  
        user = SignUpCred(**validated_data)
       
        user.save()

        return user    



class UserObjectViewSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id','fullName','email','phone','password']
        extra_kwargs = {
            'password' : {
                'write_only' : True
            }
        }


    def __str__(self):
        return f'{self.fullName} -- {self.email}'

    