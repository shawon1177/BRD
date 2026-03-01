from rest_framework.serializers import ModelSerializer
from django.contrib.auth.hashers import make_password
from driver.models import DriverModel,DriverProfile
from myapp.serializers import UserObjectViewSerializer


class DriverModelSerializer(ModelSerializer):
    class Meta:
        model = DriverModel
        fields = [
            'id',
            'FullName',
            'email',
            'describtions',
            'phone_number',
            'status',
            'DL_frontside',
            'DL_Backside',
            'NID_frontside',
            'NID_backside',
            'CV_field',
            'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'status': {'read_only': True},
        }

    def create(self, validated_data):
        user = DriverModel.objects.create(**validated_data)
        return user
    




class DriverProfileSerializer(ModelSerializer):
    user = UserObjectViewSerializer(read_only=True)
    class Meta:
        model = DriverProfile
        fields = [
            'id',
            'user',
            'DL_frontside',
            'DL_Backside',
            'NID_frontside',
            'NID_backside',
            'CV_field',
        ]


