from rest_framework import serializers
from .models import Beneficio, Plaza, Evento, Perfil, Entidad, Estamento, LugarDescuento, PublicidadMedica, ConveniosConfig, Convenio, ContactoInteres, LinkInteres
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
    # autor = UserSerializer(read_only=True) 
    #autor = UserSerializer()
    autor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Evento
        fields = '__all__'

class PublicidadMedicaSerializer(serializers.ModelSerializer):
    # autor = UserSerializer(read_only=True) 
    autor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = PublicidadMedica
        fields = '__all__'
    
class ConvenioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convenio
        fields = ('titulo', 'descripcion', 'ref', 'tipo')

class ConveniosConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConveniosConfig
        fields = ('todos_convenios_link',)
        
class ContactoInteresSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoInteres
        fields = '__all__'

class LinkInteresSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkInteres
        fields = '__all__'

