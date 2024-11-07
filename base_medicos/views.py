from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from .models import Medico, Cuota, Afiliacion, TIPOS_ESTADO_PAGO
from .serializers import MedicoSerializer, CuotaSerializer, AfiliacionSerializer
from django.db.models import Q
from .utils import convertir_fecha

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer

    @action(detail=False, methods=['post'], url_path='filtro_data_medicos')
    def filtro_data_medicos(self, request):
        """
        Endpoint para filtrar médicos por fechas de nacimiento o titulación.
        Devuelve todos los médicos si no se proporciona ningún filtro.
        Acepta fechas en formato dd-mm-aaaa y las convierte a aaaa-mm-dd.
        """
        # Obtener y convertir filtros desde el cuerpo de la solicitud (POST)
        fecha_nacimiento_inicio = convertir_fecha(request.data.get('fecha_nacimiento_inicio'))
        fecha_nacimiento_fin = convertir_fecha(request.data.get('fecha_nacimiento_fin'))
        fecha_titulo_inicio = convertir_fecha(request.data.get('fecha_titulo_inicio'))
        fecha_titulo_fin = convertir_fecha(request.data.get('fecha_titulo_fin'))

         # Obtener los filtros de afiliaciones y estados de pago
        afiliaciones = request.data.get('afiliaciones')
        estados_pago = request.data.get('estados_pago', [])
        
        # Construcción de filtros dinámicos
        filters = Q()
        aplicar_distinct = False

        # Filtrar por rango de fecha de nacimiento, si está especificado
        if fecha_nacimiento_inicio or fecha_nacimiento_fin:
            if fecha_nacimiento_inicio:
                filters &= Q(fecha_nacimiento__gte=fecha_nacimiento_inicio)
            if fecha_nacimiento_fin:
                filters &= Q(fecha_nacimiento__lte=fecha_nacimiento_fin)
        
        # Filtrar por rango de fecha de titulación, si está especificado
        if fecha_titulo_inicio or fecha_titulo_fin:
            if fecha_titulo_inicio:
                filters &= Q(fecha_titulo__gte=fecha_titulo_inicio)
            if fecha_titulo_fin:
                filters &= Q(fecha_titulo__lte=fecha_titulo_fin)

        # Filtros por afiliación
        if afiliaciones == "colmed":
            filters &= Q(afiliacion__isnull=False)
            aplicar_distinct = True
        if afiliaciones == "no_colegiado":
            filters &= Q(afiliacion__isnull=True)

        # Filtros por estados de pago, solo con estados válidos
        tipos_estado_pago_keys = [estado[0] for estado in TIPOS_ESTADO_PAGO]
        estados_validos = [estado for estado in estados_pago if estado in tipos_estado_pago_keys]
        if estados_validos:
            filters &= Q(afiliacion__estado_pago__in=estados_validos)
            
        # Si no se proporciona ningún filtro, devuelve todos los médicos
        if filters:
            medicos_filtrados = Medico.objects.filter(filters)
            if aplicar_distinct:
                medicos_filtrados = medicos_filtrados.distinct()
        else:
            medicos_filtrados = Medico.objects.all()

        serializer = self.get_serializer(medicos_filtrados, many=True)
        return Response(serializer.data)
    
    
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
    

    # @action(detail=False, methods=['get'])
    # def por_estados_pago(self, request):
    #     estados = request.query_params.getlist('pagos')
    #     if not estados:
    #         return Response({"detail": "Debe proporcionar al menos una estado de pago en los parámetros de consulta."}, status=status.HTTP_400_BAD_REQUEST)
        
    #     # Filtrar médicos que tienen afiliaciones con las entidades especificadas
    #     medicos_filtrados = Medico.objects.filter(
    #         afiliacion__estado_pago__in=estados
    #     ).distinct()
        
    #     serializer = self.get_serializer(medicos_filtrados, many=True)
    #     return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='por_afiliacion')
    def por_afiliacion(self, request):
        """
        Endpoint para filtrar médicos por Afiliación.
        Si no se proporciona ninguna afiliación, devuelve todos los médicos.
        """
        afiliaciones = request.data.get('afiliaciones', [])

        if not afiliaciones:
            medicos_filtrados = Medico.objects.all()
        else:
            medicos_filtrados = Medico.objects.filter(afiliacion__isnull=False).distinct()

        serializer = self.get_serializer(medicos_filtrados, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='por_estados_pago')
    def por_estados_pago(self, request):
        """
        Endpoint para filtrar médicos por estados de pago.
        Si no se proporciona ningún estado de pago, devuelve todos los médicos.
        """
        # Obtener lista de estados desde el cuerpo de la solicitud
        estados = request.data.get('estados', [])
        tipos_estado_pago_keys = [estado[0] for estado in TIPOS_ESTADO_PAGO]
        # Validar los estados de pago y filtrar solo los válidos
        estados_validos = [estado for estado in estados if estado in tipos_estado_pago_keys]
        
        
        # Si no se proporciona ningún estado válido, devolver todos los médicos
        if not estados_validos:
            medicos_filtrados = Medico.objects.all()
        else:
            # Filtrar médicos por los estados válidos
            medicos_filtrados = Medico.objects.filter(
                afiliacion__estado_pago__in=estados_validos
            ).distinct()
        
        serializer = self.get_serializer(medicos_filtrados, many=True)
        return Response(serializer.data)

class CuotaViewSet(viewsets.ModelViewSet):
    queryset = Cuota.objects.all()
    serializer_class = CuotaSerializer