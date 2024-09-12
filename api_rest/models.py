from django.db import models

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
    end_date = models.DateField(blank=True, null=True)

class BlacklistedAccessToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TokenGenerated(models.Model): 
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class HistorialComputer(models.Model):
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
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

