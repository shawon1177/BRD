from rest_framework.serializers import ModelSerializer
from .models import SignUpCred,MakeOrderModel
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.serializers import Serializer



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
    






class MakeOrderSerializer(serializers.ModelSerializer):
    user = UserObjectViewSerializer(read_only=True)

    class Meta:
        model = MakeOrderModel
        fields = [
            'id',
            'user',
            'location',
            'salary',
            'experience',
            'working_hour',
            'contact_number',
            'created_at',
        ]
        read_only_fields = ['user', 'contact_number', 'created_at']



class LoginSerializer(Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    