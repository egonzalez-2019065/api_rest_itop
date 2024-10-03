from django.db import models
from django.contrib.auth.models import User

from django.db import models

class Computer(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True, unique=True)
    organization_id = models.CharField(max_length=30, blank=True, null=True)
    location_id = models.CharField(max_length=30, blank=True, null=True)
    brand_id = models.CharField(max_length=30, blank=True, null=True)
    model_id = models.CharField(max_length=30, blank=True, null=True)
    osfamily_id = models.CharField(max_length=30, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)
    cpu = models.CharField(max_length=50, blank=True, null=True)
    os_version_id = models.CharField(max_length=30, blank=True, null=True)
    serialnumber = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=15, blank=True, null=True)
    ram = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=600, null=True)
    move2production = models.DateField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    end_of_warranty = models.DateField(blank=True, null=True)
    
class BlacklistedAccessToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TokenGenerated(models.Model): 
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models

class HistorialComputer(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True, unique=True)
    organization_id = models.CharField(max_length=30, blank=True, null=True)
    location_id = models.CharField(max_length=30, blank=True, null=True)
    brand_id = models.CharField(max_length=30, blank=True, null=True)
    model_id = models.CharField(max_length=30, blank=True, null=True)
    osfamily_id = models.CharField(max_length=30, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)
    cpu = models.CharField(max_length=50, blank=True, null=True)
    os_version_id = models.CharField(max_length=30, blank=True, null=True)
    serialnumber = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=15, blank=True, null=True)
    ram = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=600, null=True)
    move2production = models.DateField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    end_of_warranty = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SerialANDIdService(models.Model):
    serial_number = models.CharField(max_length=50, unique=True)
    service_id = models.PositiveIntegerField(unique=True)

class APITok(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now=True)
