from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from .models import Medico, Cuota, Afiliacion
from .serializers import MedicoSerializer, CuotaSerializer, AfiliacionSerializer
from django.db.models import Q

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer

    #Todos los médicos con alguna afiliación
    @action(detail=False, methods=['get'])
    def con_afiliacion(self, request):
        medicos_con_afiliacion = Medico.objects.filter(afiliacion__isnull=False).distinct()
        serializer = self.get_serializer(medicos_con_afiliacion, many=True)
        return Response(serializer.data)
    
    #Todos los médicos sin afiliación
    @action(detail=False, methods=['get'])
    def sin_afiliacion(self, request):
        medicos_sin_afiliacion = Medico.objects.filter(afiliacion__isnull=True)
        serializer = self.get_serializer(medicos_sin_afiliacion, many=True)
        return Response(serializer.data)

    #Las afiliaciones de un médico en específico
    @action(detail=False, methods=['get'])
    def afiliaciones(self, request, pk=None):
        medico = request.query_params.get('medico')
        afiliaciones = Afiliacion.objects.filter(medico=medico)
        serializer = AfiliacionSerializer(afiliaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_afiliacion(self, request):
        entidades = request.query_params.getlist('entidad')
        if not entidades:
            return Response({"detail": "Debe proporcionar al menos una entidad en los parámetros de consulta."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrar médicos que tienen afiliaciones con las entidades especificadas
        medicos_filtrados = Medico.objects.filter(
            afiliacion__entidad__sigla__in=entidades
        ).distinct()
        
        serializer = self.get_serializer(medicos_filtrados, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'])
    def por_estados_pago(self, request):
        estados = request.query_params.getlist('pagos')
        if not estados:
            return Response({"detail": "Debe proporcionar al menos una estado de pago en los parámetros de consulta."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrar médicos que tienen afiliaciones con las entidades especificadas
        medicos_filtrados = Medico.objects.filter(
            afiliacion__estado_pago__in=estados
        ).distinct()
        
        serializer = self.get_serializer(medicos_filtrados, many=True)
        return Response(serializer.data)

class CuotaViewSet(viewsets.ModelViewSet):
    queryset = Cuota.objects.all()
    serializer_class = CuotaSerializer