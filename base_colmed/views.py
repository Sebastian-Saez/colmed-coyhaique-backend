from rest_framework import viewsets
from .models import Beneficio, Plaza, Evento, Perfil
from .serializers import BeneficioSerializer, PlazaSerializer, EventoSerializer, PerfilSerializer

class BeneficioViewSet(viewsets.ModelViewSet):
    queryset = Beneficio.objects.all()
    serializer_class = BeneficioSerializer

class PlazaViewSet(viewsets.ModelViewSet):
    queryset = Plaza.objects.all()
    serializer_class = PlazaSerializer

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer

class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
