from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class DriverModel(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    FullName = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    describtions = models.TextField(blank=True, max_length=1000)
    phone_number = models.CharField(max_length=20,unique=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    DL_frontside = models.ImageField(upload_to='images/',default='images/default.png')
    DL_Backside = models.ImageField(upload_to='images/',default=None )
    NID_frontside = models.ImageField(upload_to='images/', default=None)
    NID_backside = models.ImageField(upload_to='images/', default=None)
    CV_field = models.ImageField(upload_to="images/", default=None)
    is_varified = models.BooleanField(default=False)
  




class DriverOtp(models.Model):
    user = models.OneToOneField(DriverModel,on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15,blank=True)
    phone_otp = models.CharField(max_length=6,blank=True)
    is_varified = models.BooleanField(default=False)
    attemps = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def can_resend(self):
     return timezone.now() >= self.created_at + timedelta(seconds=60)
    
    def resed_timeout(self):
      remainingtime =(self.created_at + timedelta(seconds=60)) - timezone.now()
      return max(int(remainingtime.total_seconds()),0)




class DriverEmail(models.Model):
    user = models.ForeignKey(DriverModel,on_delete=models.CASCADE)
    email = models.EmailField(unique=True,default=None)
    EmialOtp = models.CharField(max_length=6,blank=True)
    is_varified = models.BooleanField(default=False)
    attemps = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    def can_resend(self):
        return timezone.now() >= self.created_at + timedelta(seconds=60)
    
    def resend_timeout(self):
        time_limite = (self.created_at + timedelta(seconds=60)) - timezone.now()
        return max(int(time_limite.total_seconds()),0)





class DriverProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='driver_profile')
    describtions = models.TextField(blank=True, max_length=1000)
    DL_frontside = models.ImageField(upload_to='images/',default='images/default.png')
    DL_Backside = models.ImageField(upload_to='images/',default=None )
    NID_frontside = models.ImageField(upload_to='images/', default=None)
    NID_backside = models.ImageField(upload_to='images/', default=None)
    CV_field = models.ImageField(upload_to="images/", default=None)
    is_booked  = models.BooleanField(default=False)





