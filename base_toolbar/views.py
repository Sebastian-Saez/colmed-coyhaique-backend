from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from base_colmed.authentication import CookieJWTAuthentication
from .models import (
    MisionVision, NormativaItem, DirectivaMember,
    Departamento, AgrupacionRegional, Capitulo,
    TribunalEtica,
    PaymentInfo, CasaMedicoInfo, ColegiarseInfo
)
from .serializers import (
    MisionVisionSerializer, NormativaItemSerializer, DirectivaMemberSerializer,
    DepartamentoSerializer, AgrupacionRegionalSerializer, CapituloSerializer,
    TribunalEticaSerializer,
    PaymentInfoSerializer, ColegiarseInfoSerializer, CasaMedicoInfoSerializer
)

from base_colmed.models import LinkInteres, ContactoInteres, ConveniosConfig, Convenio
from base_colmed.serializers import LinkInteresSerializer, ContactoInteresSerializer, ConveniosConfigSerializer, ConvenioSerializer


class PaymentInfoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentInfo.objects.all().order_by('-fecha_modificacion')
    serializer_class = PaymentInfoSerializer

    @action(detail=False, methods=['get'])
    def informacion_pagos(self, request):
        """Devuelve el registro más reciente (singleton)."""
        obj = self.get_queryset().first()
        return Response(self.get_serializer(obj).data)
    
class ColegiarseInfoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ColegiarseInfo.objects.all().order_by('-fecha_modificacion')
    serializer_class = ColegiarseInfoSerializer

    @action(detail=False, methods=['get'])
    def colegiarse(self, request):
        obj = self.get_queryset().first()
        return Response(self.get_serializer(obj).data)


class CasaMedicoInfoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CasaMedicoInfo.objects.all().order_by('-fecha_modificacion')
    serializer_class = CasaMedicoInfoSerializer

    @action(detail=False, methods=['get'])
    def casa_medico(self, request):
        obj = self.get_queryset().first()
        return Response(self.get_serializer(obj).data)

class MisionVisionViewSet(viewsets.ModelViewSet):
    queryset = MisionVision.objects.all()
    serializer_class = MisionVisionSerializer

    @action(detail=False, methods=['get'])
    def mision_vision(self, request):
        """Obtener la misión y visión vigente."""
        mv = MisionVision.objects.last()
        serializer = self.get_serializer(mv)
        return Response(serializer.data)
    

class NormativaViewSet(viewsets.ModelViewSet):
    queryset = NormativaItem.objects.all()
    serializer_class = NormativaItemSerializer

    @action(detail=False, methods=['get'])
    def todas_normativas(self, request):
        """Obtener todas las normativas."""
        items = NormativaItem.objects.order_by('id')
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

class DirectivaViewSet(viewsets.ModelViewSet):
    queryset = DirectivaMember.objects.all()
    serializer_class = DirectivaMemberSerializer

    @action(detail=False, methods=['get'])
    def directiva(self, request):
        """Obtener todos los miembros de directiva."""
        members = DirectivaMember.objects.order_by('id')
        serializer = self.get_serializer(members, many=True)
        return Response(serializer.data)

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer

    @action(detail=False, methods=['get'])
    def todos_departamentos(self, request):
        deps = Departamento.objects.order_by('id')
        serializer = self.get_serializer(deps, many=True)
        return Response(serializer.data)

class AgrupacionRegionalViewSet(viewsets.ModelViewSet):
    queryset = AgrupacionRegional.objects.all()
    serializer_class = AgrupacionRegionalSerializer

    @action(detail=False, methods=['get'])
    def todas_agrupaciones(self, request):
        ags = AgrupacionRegional.objects.order_by('id')
        serializer = self.get_serializer(ags, many=True)
        return Response(serializer.data)

class CapituloViewSet(viewsets.ModelViewSet):
    queryset = Capitulo.objects.all()
    serializer_class = CapituloSerializer

    @action(detail=False, methods=['get'])
    def todos_capitulos(self, request):
        caps = Capitulo.objects.order_by('id')
        serializer = self.get_serializer(caps, many=True)
        return Response(serializer.data)

class TribunalEticaViewSet(viewsets.ModelViewSet):
    queryset = TribunalEtica.objects.all()
    serializer_class = TribunalEticaSerializer

    @action(detail=False, methods=['get'])
    def tribunal_etica(self, request):
        """Obtener tribunal de ética y su directiva."""
        tribunal = TribunalEtica.objects.last()
        serializer = self.get_serializer(tribunal)
        return Response(serializer.data)


# ---------------------------------
# CREATE / UPDATE API VIEWS (POST)
# ---------------------------------
@method_decorator(csrf_exempt, name='dispatch')
class SomosCreateUpdateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    model_map = {
        'misionvision': (MisionVision, MisionVisionSerializer),
        'normativa': (NormativaItem, NormativaItemSerializer),
        'directiva': (DirectivaMember, DirectivaMemberSerializer),
        'departamentos': (Departamento, DepartamentoSerializer),
        'agrupaciones': (AgrupacionRegional, AgrupacionRegionalSerializer),
        'capitulos': (Capitulo, CapituloSerializer),
        'tribunal_etica': (TribunalEtica, TribunalEticaSerializer),
        'links_web': (LinkInteres, LinkInteresSerializer),
        'contactos': (ContactoInteres, ContactoInteresSerializer),
        'convenios': (Convenio, ConvenioSerializer),
        'convenios_config': (ConveniosConfig, ConveniosConfigSerializer),
        'pagos' : (PaymentInfo, PaymentInfoSerializer),
        'colegiarse' : (ColegiarseInfo, ColegiarseInfoSerializer),
        'casa_medico' : (CasaMedicoInfo, CasaMedicoInfoSerializer),
    }

    def post(self, request, section):
        """
        Crear o actualizar datos de la sección indicada en 'section'.
        'section' se corresponde con la clave en model_map.
        """
        if section not in self.model_map:
            return Response({'detail':'Sección inválida'}, status=status.HTTP_400_BAD_REQUEST)

        Model, Serializer = self.model_map[section]
        payload = request.data

        # Asegurarnos de trabajar con lista
        items = payload if isinstance(payload, list) else [payload]

        existing_ids = set(Model.objects.values_list('id', flat=True))

        results = []
        errors = []
        processed_ids = set()

        for idx, data in enumerate(items):
            obj_id = data.get('id', None)
            if obj_id:
                # actualizar
                try:
                    instance = Model.objects.get(id=obj_id)
                    serializer = Serializer(instance, data=data, partial=True)
                except Model.DoesNotExist:
                    errors.append({
                        'index': idx,
                        'detail': f'{section} id={obj_id} no encontrado.'
                    })
                    continue
            else:
                # crear
                serializer = Serializer(data=data)

            if serializer.is_valid():
                obj = serializer.save()
                results.append(Serializer(obj).data)
                processed_ids.add(obj.id)
            else:
                errors.append({
                    'index': idx,
                    'errors': serializer.errors
                })

        to_delete = existing_ids - processed_ids
        if to_delete:
            Model.objects.filter(id__in=to_delete).delete()

        status_code = status.HTTP_200_OK
        if errors and not results:
            status_code = status.HTTP_400_BAD_REQUEST
        elif errors and results:
            status_code = status.HTTP_207_MULTI_STATUS  # varios resultados

        return Response({
            'results': results,
            'errors': errors
        }, status=status_code)



        # if obj_id:
        #     # update existing
        #     try:
        #         instance = Model.objects.get(id=obj_id)
        #     except Model.DoesNotExist:
        #         return Response({'detail':'Elemento no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        #     serializer = Serializer(instance, data=data, partial=True)
        # else:
        #     # create new
        #     serializer = Serializer(data=data)

        # if serializer.is_valid():
        #     obj = serializer.save()
        #     return Response(Serializer(obj).data, status=status.HTTP_200_OK)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)