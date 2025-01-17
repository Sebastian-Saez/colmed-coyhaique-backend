from rest_framework import serializers
from .models import Medico, Cuota, Afiliacion, Institucion,Especialidad,RegistroSuperintendencia, OrdenProfesional
from base_colmed.serializers import UserSerializer, PlazaSerializer, EntidadSerializer, EstamentoSerializer, LugarDescuentoSerializer



class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = '__all__'

class InstitucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institucion
        fields = '__all__'

class EspecialidadSerializer(serializers.ModelSerializer):
    institucion_certificadora = InstitucionSerializer(read_only=True)
    class Meta:
        model = Especialidad
        fields = '__all__'

class OrdenProfesionalSerializer(serializers.ModelSerializer):
    institucion_certificadora = InstitucionSerializer(read_only=True)
    class Meta:
        model = OrdenProfesional
        fields = '__all__'

class RegistroSuperintendenciaSerializer(serializers.ModelSerializer):
    ordenes_profesionales = OrdenProfesionalSerializer(many=True, read_only=True)
    especialidades = EspecialidadSerializer(many=True, read_only=True) 
    class Meta:
        model = RegistroSuperintendencia
        fields = '__all__'

class AfiliacionSerializer(serializers.ModelSerializer):
    entidad = EntidadSerializer(read_only=True)
    estamento = EstamentoSerializer(read_only=True)
    lugar_descuento = LugarDescuentoSerializer(read_only=True)
    estado_pago = serializers.CharField(source='get_estado_pago_display')
    
    class Meta:
        model = Afiliacion
        fields = '__all__'

class MedicoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plaza = PlazaSerializer(read_only=True)
    afiliaciones = AfiliacionSerializer(source='afiliacion_set', many=True, read_only=True)
    
    class Meta:
        model = Medico
        fields = '__all__'