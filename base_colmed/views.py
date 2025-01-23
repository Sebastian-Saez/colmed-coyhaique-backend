from rest_framework import viewsets
from django.contrib.auth import logout
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import Beneficio, Plaza, Evento, Perfil
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import BeneficioSerializer, PlazaSerializer, EventoSerializer, PerfilSerializer
from django.utils.translation import gettext_lazy as _
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.serializers import JWTSerializer
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from google.auth.transport import requests
from google.oauth2 import id_token
from backend_colmed.settings import GOOGLE_CLIENT_ID

class BeneficioViewSet(viewsets.ModelViewSet):
    queryset = Beneficio.objects.all()
    serializer_class = BeneficioSerializer

    @action(detail=False, methods=['get'])
    def todos_beneficios(self, request):
        """Endpoint para obtener todos los beneficios activos."""
        fecha_actual = timezone.now().date()
        beneficios_activos = Beneficio.objects.filter(fecha_baja__isnull=True) | Beneficio.objects.filter(fecha_baja__gte=fecha_actual)
        serializer = self.get_serializer(beneficios_activos, many=True)
        return Response(serializer.data)
    
class PlazaViewSet(viewsets.ModelViewSet):
    queryset = Plaza.objects.all()
    serializer_class = PlazaSerializer

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer

    @action(detail=False, methods=['get'])
    def eventos_base(self, request):
        """Endpoint para obtener todas las noticias activas que no sean destacadas."""
        eventos = Evento.objects.all().order_by('-fecha_inicio')
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data)
    
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
            
            # # Obtener el perfil del usuario
            # profile = Perfil.objects.get(user=user)
             # Obtener los perfiles del usuario
            profiles = Perfil.objects.filter(user=user)
            profiles_data = PerfilSerializer(profiles, many=True).data

            return Response({
                'access': str(refresh.access_token),  # Token de acceso
                'refresh': str(refresh),              # Token de refresco
                'user': {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    # 'perfil': profile.tipo_perfil,
                    'perfiles': profiles_data,
                    #'permissions': list(user.get_all_permissions()),
                }
            })
        else:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)



class UpdatePasswordView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get('email')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        # Validar que todos los campos estén presentes
        if not email or not old_password or not new_password:
            return Response({"detail": _("All fields are required.")}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el usuario exista
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": _("Invalid email address.")}, status=status.HTTP_404_NOT_FOUND)

        # Verificar que el usuario autenticado sea el propietario del email proporcionado
        # if request.user != user:
        #     return Response({"detail": _("You are not authorized to change this password.")}, status=status.HTTP_403_FORBIDDEN)

        # Autenticar al usuario con la contraseña anterior
        user = authenticate(username=user.username, password=old_password)
        if user is None:
            return Response({"detail": _("Old password is incorrect.")}, status=status.HTTP_401_UNAUTHORIZED)

        # Validar que la nueva contraseña no sea igual a la anterior
        if old_password == new_password:
            return Response({"detail": _("New password must be different from the old password.")}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar la contraseña
        user.set_password(new_password)
        user.save()

        # Regenerar tokens de acceso y refresco
        refresh = RefreshToken.for_user(user)

        return Response({
            "detail": _("Password updated successfully."),
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
        }, status=status.HTTP_200_OK)

# class GoogleLogin(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     client_class = OAuth2Client
#     serializer_class = JWTSerializer  # asume que estás usando JWT

#     def post(self, request, *args, **kwargs):
#         # Llama a la implementación base
#         print("Request??? ", request,"\n")
#         response = super().post(request, *args, **kwargs)
#         print("Response??? : ", response,"\n")
#         user = request.user
#         if not user or not user.is_authenticated:
#             # Si por alguna razón no se autenticó el usuario
#             return Response({"detail": "User not authorized."}, status=status.HTTP_401_UNAUTHORIZED)
        
#         # Aquí el usuario está autenticado, es decir existe en tu BD.
#         # Obtenemos los perfiles asociados
#         profiles = Perfil.objects.filter(user=user)
#         profiles_data = PerfilSerializer(profiles, many=True).data
        
#         # response.data debería contener tokens de acceso (y refresh) generados por dj_rest_auth
#         # Vamos a modificar la respuesta para agregar la info del usuario y sus perfiles
#         new_data = dict(response.data)  # copia de los datos originales
#         new_data['user'] = {
#             'username': user.username,
#             'email': user.email,
#             'perfiles': profiles_data
#         }
        
#         # Actualizar la data de la respuesta
#         response.data = new_data
#         return response

class GoogleLogin(APIView):
    """
    Recibe un id_token (credential) de Google, valida el token,
    verifica existencia del usuario en BD, genera tokens JWT propios.
    """
    def post(self, request):
        id_token_google = request.data.get('id_token')
        if not id_token_google:
            return Response({"detail": "id_token is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # idinfo = id_token.verify_oauth2_token(id_token_google, requests.Request(), GOOGLE_CLIENT_ID)
        
        # Validar el id_token con Google
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_google,
                requests.Request(),
                GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=300  # tolerancia de 5 minutos
            )
            
            # Si la validación es exitosa, idinfo contendrá el email del usuario.
            email = idinfo.get('email')
            if not email:
                return Response({"detail": "Invalid token: no email found."}, status=status.HTTP_400_BAD_REQUEST)
            
            if idinfo['aud'] != GOOGLE_CLIENT_ID:
                return Response({"detail": "Invalid audience."}, status=status.HTTP_401_UNAUTHORIZED)
            name_google = idinfo.get('name')
            picture_google = idinfo.get('picture')
        except ValueError:
            # Token inválido
            return Response({"detail": "Invalid id_token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Verificar si el usuario existe en la BD
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not authorized."}, status=status.HTTP_401_UNAUTHORIZED)

        # Obtener perfiles del usuario
        perfiles = Perfil.objects.filter(user=user)
        perfiles_data = PerfilSerializer(perfiles, many=True).data

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "access": access_token,
            "refresh": refresh_token,
            "user": {
                "username": user.username,
                "email": user.email,
                "perfiles": perfiles_data,
                "name_google" : name_google,
                "picture": picture_google
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Endpoint para cerrar sesión.
    Elimina el token JWT de acceso en el frontend y revoca el refresh token en el backend.
    """

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Revoca el refresh token

            return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Error during logout"}, status=status.HTTP_400_BAD_REQUEST)