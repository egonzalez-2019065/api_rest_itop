from django.contrib.auth.models import User
from .models import Computer, TokenGenerated, HistorialComputer
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class ComputerSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Computer
        fields = '__all__'

class TokenGeneratedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenGenerated
        fields = '__all__'

class HistorialComputerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialComputer
        fields = '__all__'
