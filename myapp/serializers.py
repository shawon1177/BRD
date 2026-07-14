from rest_framework.serializers import ModelSerializer
from .models import SignUpCred,MakeOrderModel,UserProfile
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.serializers import Serializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from myapp.permissions.permissions import OnlyOwnerAndAdmin
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

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






class UpdateProfileApiView(APIView):
    permission_classes = [IsAuthenticated, OnlyOwnerAndAdmin]

    def put(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)

        serializer = UploadUserProfileViewSerializer(
            profile,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Profile updated successfully",
                "serializer": UserProfileViewSerializer(
                    profile,
                    context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )
    





class UserProfileViewSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "user", "bio", "profile_picture"]
        read_only_fields = ["id", "user"]

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None    



class UserObjectViewSerializer(ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'fullName', 'email', 'phone', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return UserProfileViewSerializer(obj.profile, context=self.context).data
        return None



class UploadUserProfileViewSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'profile_picture']
        read_only_fields = ['user', 'id']






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






class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'fullName', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)    
    
    