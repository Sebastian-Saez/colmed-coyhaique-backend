from rest_framework import viewsets
from django.contrib.auth import logout
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import Beneficio, Plaza, Evento, Perfil
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
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

    
@login_required
def user_profile(request):
    perfil = Perfil.objects.get(user=request.user)
    return JsonResponse({
        'usuario': request.user.username,
        'tipo_perfil': perfil.tipo_perfil,
        'activo': perfil.activo,
    })


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=user.username, password=password)

        if user is not None:
            if not user.is_active:
                return Response({"detail": "Account is deactivated."}, status=status.HTTP_403_FORBIDDEN)
            
            # Crear los tokens de acceso y refresco
            refresh = RefreshToken.for_user(user)
            
            # Obtener el perfil del usuario
            profile = Perfil.objects.get(user=user)

            return Response({
                'access': str(refresh.access_token),  # Token de acceso
                'refresh': str(refresh),              # Token de refresco
                'user': {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'perfil': profile.tipo_perfil,
                    #'permissions': list(user.get_all_permissions()),
                }
            })
        else:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
