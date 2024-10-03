from django.contrib.auth.models import User
from .models import PComputer, AuthGenerated, HistorialPComputer
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class ComputerSerializer(serializers.ModelSerializer):
    class Meta: 
        model = PComputer
        fields = '__all__'
    
class TokenGeneratedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthGenerated
        fields = '__all__'

class HistorialComputerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialPComputer
        fields = '__all__'
