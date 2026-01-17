from driver.models import DriverModel
from rest_framework.serializers import ModelSerializer


class DriverModelSerializer(ModelSerializer):
    class Meta:
        model = DriverModel
        fields = ['FullName','email','describtions','phone_number','status','DL_frontside','DL_Backside','NID_frontside','NID_backside','CV_field']
        extra_kwargs = {
            'password':{
                'write_only':True
            }
        }
