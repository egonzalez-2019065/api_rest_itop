from django.db import models
from django.utils import timezone

class Computer(models.Model):
    name = models.CharField(max_length=60, blank=True, null=True, unique=True)
    organization_name = models.CharField(max_length=60, blank=True, null=True)
    location_name = models.CharField(max_length=60, blank=True, null=True)
    brand_name = models.CharField(max_length=40, blank=True, null=True)
    model_name = models.CharField(max_length=40, blank=True, null=True)
    osfamily_name = models.CharField(max_length=40, blank=True, null=True)
    type = models.CharField(max_length=40, blank=True, null=True)
    cpu = models.CharField(max_length=40, blank=True, null=True)
    os_version_name = models.CharField(max_length=40, blank=True, null=True)
    serialnumber = models.CharField(max_length=40, unique=True, default='')
    status = models.CharField(max_length=10, blank=True, null=True)
    ram = models.PositiveIntegerField(blank=True, null=True) 
    description = models.CharField(max_length=500, null=True)
    move2production = models.DateField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    end_of_warranty = models.DateField(blank=True, null=True)
    

class BlacklistedAccessToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TokenGenerated(models.Model): 
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class HistorialComputer(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True, unique=True)
    organization_name = models.CharField(max_length=50, blank=True, null=True)
    location_name = models.CharField(max_length=50, blank=True, null=True)
    brand_name = models.CharField(max_length=30, blank=True, null=True)
    model_name = models.CharField(max_length=30, blank=True, null=True)
    osfamily_name = models.CharField(max_length=30, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)
    cpu = models.CharField(max_length=50, blank=True, null=True)
    os_version_name = models.CharField(max_length=50, blank=True, null=True)
    serialnumber = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=15, blank=True, null=True)
    ram = models.PositiveIntegerField(blank=True, null=True) 
    description = models.CharField(max_length=600, null=True)
    move2production = models.DateField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    end_of_warranty = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class SerialAndIDItop(models.Model):
    serial_number = models.CharField(max_length=50, unique=True)
    id_itop = models.PositiveIntegerField(unique=True)

