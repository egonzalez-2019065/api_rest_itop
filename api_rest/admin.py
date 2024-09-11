from django.contrib import admin
from .models import Computer

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'serial_number', 'status', 'purchase_date')
    search_fields = ('hostname', 'serial_number')


