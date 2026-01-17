from django.db import models




class DriverModel(models.Model):
    STATUS_CHOISE = (
        ("pending","Pending",),
        ("accepted",'Accepted',),
        ("rejected",'Rejected')
    )

    FullName = models.CharField(max_length=255,blank=True)
    email = models.EmailField(max_length=255,unique=True)
    password = models.CharField(max_length=255,blank=True)
    describtions = models.TextField(blank=True,max_length=1000)
    phone_number = models.CharField(max_length=20)
    status  = models.CharField(choices=STATUS_CHOISE,default="pending")


    DL_frontside = models.ImageField(upload_to='images/')
    DL_Backside = models.ImageField(upload_to='images/')
    NID_frontside = models.ImageField(upload_to='images/')
    NID_backside = models.ImageField(upload_to='images/')
    CV_field = models.ImageField(upload_to="images/")