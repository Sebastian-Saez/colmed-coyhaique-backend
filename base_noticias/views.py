from rest_framework import viewsets
from .models import Noticia
from .serializers import NoticiaSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.all()
    serializer_class = NoticiaSerializer

    @action(detail=False, methods=['get'])
    def noticias_destacadas(self, request):
        """Endpoint para obtener todas las noticias destacadas y activas."""
        destacadas = Noticia.objects.filter(activo=True, destacada=True).order_by('-id')
        serializer = self.get_serializer(destacadas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def noticias_base(self, request):
        """Endpoint para obtener todas las noticias activas que no sean destacadas."""
        no_destacadas = Noticia.objects.filter(activo=True, destacada=False).order_by('-id')
        serializer = self.get_serializer(no_destacadas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def todas_noticias(self, request):
        """Endpoint para obtener todas las noticias activas."""
        noticias = Noticia.objects.filter(activo=True).order_by('-id')
        serializer = self.get_serializer(noticias, many=True)
        return Response(serializer.data)