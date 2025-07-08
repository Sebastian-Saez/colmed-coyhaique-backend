
from rest_framework import serializers
from .models import (
    MisionVision, NormativaItem, DirectivaMember,
    Departamento, AgrupacionRegional, Capitulo,
    TribunalEtica, TribunalMember, 
    CasaMedicoInfo, ColegiarseInfo, PaymentInfo
)

class MisionVisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MisionVision
        fields = '__all__'


class NormativaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormativaItem
        fields = '__all__'


class DirectivaMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectivaMember
        fields = '__all__'


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'


class AgrupacionRegionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgrupacionRegional
        fields = '__all__'


class CapituloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capitulo
        fields = '__all__'


class TribunalMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TribunalMember
        fields = ['id', 'cargo', 'persona']


class TribunalEticaSerializer(serializers.ModelSerializer):
    directiva = TribunalMemberSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = TribunalEtica
        fields = ['id', 'descripcion', 'directiva']

    # def to_representation(self, instance):
    #     # Usar representación por defecto, sin create/update
    #     return super().to_representation(instance)
    
     # -------- CREAR --------
    def create(self, validated_data):
        miembros_data = validated_data.pop('directiva', [])
        tribunal = TribunalEtica.objects.create(**validated_data)

        for miembro in miembros_data:
            TribunalMember.objects.create(tribunal=tribunal, **miembro)

        return tribunal

    # -------- ACTUALIZAR --------
    def update(self, instance, validated_data):
        miembros_data = validated_data.pop('directiva', None)

        # actualizar la descripción
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.save()

        # si viene lista de miembros, reemplazarla por completo
        if miembros_data is not None:
            instance.directiva.all().delete()
            for miembro in miembros_data:
                TribunalMember.objects.create(tribunal=instance, **miembro)

        return instance

#Módulo de "SERVICIOS"
class PaymentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PaymentInfo
        fields = '__all__'


class ColegiarseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ColegiarseInfo
        fields = '__all__'


class CasaMedicoInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CasaMedicoInfo
        fields = '__all__'