from django.db import models

# Create your models here.
class Computer(models.Model):
    hostname = models.CharField(max_length=50, blank=True, null=True, unique=True)
    organization = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    marca = models.CharField(max_length=30, blank=True, null=True)
    modelo = models.CharField(max_length=30, blank=True, null=True)
    os_system = models.CharField(max_length=30, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)
    processor = models.CharField(max_length=50, blank=True, null=True)
    os_version = models.CharField(max_length=50, blank=True, null=True)
    serial_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    ram = models.PositiveIntegerField(blank=True, null=True) 
    disk_capacity = models.CharField(max_length=10, blank=True, null=True)
    disk_free = models.CharField(max_length=10, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True),
    unique_token = models.CharField(max_length=100, blank=False, null=False, unique=True)