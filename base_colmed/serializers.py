from rest_framework import serializers
from .models import Beneficio, Plaza, Evento, Perfil
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = '__all__'

class BeneficioSerializer(serializers.ModelSerializer):
    usuario_modificacion = UserSerializer(read_only=True) 

    class Meta:
        model = Beneficio
        fields = '__all__'

class PlazaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plaza
        fields = '__all__'

class EventoSerializer(serializers.ModelSerializer):
    autor = UserSerializer(read_only=True) 
    
    class Meta:
        model = Evento
        fields = '__all__'

