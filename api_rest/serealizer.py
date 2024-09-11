from django.contrib.auth.models import User
from .models import Computer
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class ComputerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta: 
        model = Computer
        fields = '__all__'