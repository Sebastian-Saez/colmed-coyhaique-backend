from rest_framework import serializers
from .models import Beneficio, Plaza, Evento, Perfil, Entidad, Estamento, LugarDescuento
from django.contrib.auth.models import User

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    perfiles = PerfilSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'perfiles']

class BeneficioSerializer(serializers.ModelSerializer):
    usuario_modificacion = UserSerializer(read_only=True) 

    class Meta:
        model = Beneficio
        fields = '__all__'

class PlazaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plaza
        fields = '__all__'

class EstamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estamento
        fields = '__all__'

class LugarDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LugarDescuento
        fields = '__all__'

class EntidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entidad
        fields = '__all__'

class EventoSerializer(serializers.ModelSerializer):
    autor = UserSerializer(read_only=True) 
    
    class Meta:
        model = Evento
        fields = '__all__'

