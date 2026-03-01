from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class HireConfirmationModel(models.Model):
    STATUS_CODE = (
        ('pending','Pending'),
        ('accepted','Accepted'),
        ('rejected','Rejected')
    )
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='customer')
    driver = models.ForeignKey(User,on_delete=models.CASCADE,related_name='driver')
    confirmation_fee = models.DecimalField(max_digits=4,decimal_places=2,default=2000.00)
    is_confirm = models.BooleanField(default=False)
    joining_month = models.TextField(max_length=1000,blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CODE,default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.user} -- {self.driver}'
    
    


class DriverBookingModel(models.Model):
    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_side')
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='driver_side')
    booking_status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    


class DriverConfirmationModel(models.Model): 
   confirmation_payment = models.DecimalField(max_digits=10, decimal_places=2)
   user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_confirmation')
   driver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirmation')
   payment_confirmation = models.BooleanField(default=False)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   def __str__(self):
       return f"Confirmation for {self.user.email} - {self.driver.FullName}"
   



class DriverAndUserServiceHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_service_history')
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='driver_service_history')
    service_duration = models.CharField(max_length=100,default=None)
    service_months = models.IntegerField(default=None)
    service_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Service History for {self.user.eTruemail} - {self.driver.FullName}"


