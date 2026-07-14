from django.utils import timezone
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from datetime import timedelta


class BaseUserManagerCustom(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)   
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
      extra_fields.setdefault('is_superuser', True)
      extra_fields.setdefault('is_staff', True)
      extra_fields.setdefault('is_active', True)
  
      if extra_fields.get('is_staff') is not True:
          raise ValueError("Superuser must have is_staff=True.")
      if extra_fields.get('is_superuser') is not True:
          raise ValueError("Superuser must have is_superuser=True.")
  
      return self.create_user(email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    fullName = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    is_driver = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BaseUserManagerCustom()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullName']

    def __str__(self):
        return self.email






class SignUpCred(models.Model):
    STATUS_CODE = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    fullName = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20,unique=True,default=None)
    pasword = models.CharField(max_length=120,default=None)
    status = models.CharField(max_length=20, choices=STATUS_CODE, default="pending")

    def __str__(self):
        return self.email

    


class UserOtp(models.Model):
    user = models.ForeignKey(SignUpCred,on_delete=models.CASCADE)
    PhoneOtp = models.CharField(max_length=6,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    



    def can_resend(self):
        return timezone.now() >= self.created_at + timedelta(seconds=60)
    

    def resend_timeout(self):
        remainingtime =(self.created_at + timedelta(seconds=60)) - timezone.now()
        return max(int(remainingtime.total_seconds()),0)
    
    

    def __str__(self):
        return f'{self.EmailOtp} and {self.PhoneOtp} for {self.user.email}'



class EmailOtp(models.Model):
    user = models.ForeignKey(SignUpCred,on_delete=models.CASCADE)
    EmialOtp = models.CharField(max_length=6,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def Email_otp_NotExpired(self):
      return timezone.now() >= self.created_at + timedelta(seconds=60)
    
    def remaining_time(self):
        time_limite = (self.created_at + timedelta(seconds=60)) - timezone.now()
        return max(int(time_limite.total_seconds()),0)
    
    def __str__(self):  
        return f'{self.EmailOtp} and {self.PhoneOtp} for {self.user.email}'
    

class ForgetPasswordModel(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    email = models.EmailField(max_length=255,blank=True,null=True)  
    phone = models.CharField(max_length=15,blank=True,null=True)  
    otp = models.CharField(max_length=6,null=6)
    attemps =models.IntegerField(default=0)
    otp_varified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def can_resend(self):
        return timezone.now() >= self.created_at + timedelta(seconds=60)
    
    def remaining_time(self):
        remaining = (self.created_at + timedelta(seconds=60)) - timezone.now()
        return max(int(remaining.total_seconds()),0)

    def __str__(self):
        return f'{self.user} -- {self.email}'
    


class MakeOrderModel(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='customer_order')
    location = models.TextField(max_length=1000,blank=True)
    salary = models.DecimalField(max_digits=15,decimal_places=2,blank=True)
    experience = models.CharField(max_length=255,blank=True)
    working_hour = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15,default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} -- {self.location}'
    




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)

    def __str__(self):
        return f'Profile of {self.user.email}'
    


class LocationViewModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_locations',default=None)
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Location of {self.user.email}: {self.location_name}'