from rest_framework import serializers
from .models import Medico, Cuota
from base_colmed.serializers import UserSerializer

class MedicoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Medico
        fields = '__all__'

class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = '__all__'