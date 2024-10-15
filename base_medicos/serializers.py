from rest_framework import serializers
from .models import Medico, Cuota, Afiliacion
from base_colmed.serializers import UserSerializer, PlazaSerializer, EntidadSerializer, EstamentoSerializer, LugarDescuentoSerializer

class MedicoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plaza = PlazaSerializer(read_only=True)
    class Meta:
        model = Medico
        fields = '__all__'

class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = '__all__'

class AfiliacionSerializer(serializers.ModelSerializer):
    entidad = EntidadSerializer(read_only=True)
    estamento = EstamentoSerializer(read_only=True)
    lugar_descuento = LugarDescuentoSerializer(read_only=True)
    estado_pago = serializers.CharField(source='get_estado_pago_display')
    
    class Meta:
        model = Afiliacion
        fields = '__all__'