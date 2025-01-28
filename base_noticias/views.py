from rest_framework import viewsets,status
import json
from rest_framework.views import APIView
from .models import Noticia
from .serializers import NoticiaSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from base_colmed.authentication import CookieJWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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

@method_decorator(csrf_exempt, name='dispatch')
class NoticiaCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        """
        Endpoint para crear o actualizar una noticia.
        Si el autor está presente en el request, se actualiza la noticia existente.
        Si el autor no está presente, se crea una nueva noticia.
        """
        
        data = request.data.copy()
        autor_id = data.get('autor')
        try:
            autor = User.objects.get(id=autor_id) if autor_id else request.user
        except User.DoesNotExist:
            return Response({"detail": "Autor no válido."}, status=status.HTTP_400_BAD_REQUEST)

        # Convertir valores booleanos desde cadenas "true" y "false"
        if 'destacada' in data:
            data['destacada'] = data.get('destacada') == 'true'
        if 'activo' in data:
            data['activo'] = data.get('activo') == 'true'

        # Validar el campo link si existe y tiene un formato adecuado
        if data.get('link') != "null":
            
            try:
                data['link'] = json.dumps({"link": data.get('link')})
            except ValueError:
                return Response({"detail": "El campo 'link' debe ser un objeto JSON válido con el formato {'link': url}"}, status=status.HTTP_400_BAD_REQUEST)

        if data.get('id'):
            # Actualizar la noticia existente
            try:
                noticia = Noticia.objects.get(id=data.get('id'))
                data['autor'] = int(autor_id)
                serializer = NoticiaSerializer(noticia, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Noticia.DoesNotExist:
                return Response({"detail": "Noticia no encontrada para el autor especificado."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Crear una nueva noticia
            data['autor'] = int(autor_id)
            serializer = NoticiaSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)