from rest_framework import serializers
from django.contrib.auth import get_user_model
from driver.models import DriverProfile
from myapp.models import MakeOrderModel
from .models import DriverConfirmationModel,HireConfirmationModel,DriverBookingModel



class DriverProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = [
            'id',
            'DL_frontside',
            'is_booked'
            
        ]

    def get_image(self,obj):
            request = self.context.get('request')

            if obj.DL_frontside:
                return request.build_absolute_uri(obj.DL_frontside.url)
            return None
        




User = get_user_model()

class UserViewSerializer(serializers.ModelSerializer):
    driver_profile = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id','fullName','email','phone','driver_profile']


    def get_driver_profile(self,obj):
        if hasattr(obj,'driver_profile'):
            return DriverProfileViewSerializer(
                obj.driver_profile,
                context = self.context
            ).data
        return None    








class CustomerOrderViewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MakeOrderModel
        fields = [
            'id',
            'location',
            'salary',
            'experience',
            'working_hour',
            'contact_number',
            'created_at',
            
        ]

   
    

User = get_user_model()

class CarUserViewSerializer(serializers.ModelSerializer):
    customer_order = serializers.SerializerMethodField() 
    class Meta:
        model = User
        fields = ['id', 'fullName', 'email', 'phone', 'customer_order']

    
    def get_customer_order(self, obj):
        if hasattr(obj, 'customer_order'):  
            return CustomerOrderViewSerializer(
                obj.customer_order,
                context=self.context
            ).data
        return None
    


class DriverBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverBookingModel
        fields = ['id', 'user', 'driver', 'booking_status', 'created_at', 'updated_at']




class HireConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HireConfirmationModel
        fields = ['id', 'user', 'driver', 'booking_status', 'created_at', 'updated_at']
        


class DriverConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverConfirmationModel
        fields = ['id', 'user', 'driver', 'booking_status', 'created_at', 'updated_at']