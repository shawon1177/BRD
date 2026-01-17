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
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    fullName = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

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