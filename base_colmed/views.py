from rest_framework import viewsets
from django.contrib.auth import logout
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import Beneficio, Plaza, Evento, Perfil, PublicidadMedica, Convenio, ConveniosConfig, ContactoInteres,LinkInteres
from base_medicos.models import Medico, MedicoAppMovil, PasswordResetToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import BeneficioSerializer, PlazaSerializer, EventoSerializer, PerfilSerializer, PublicidadMedicaSerializer, ConveniosConfigSerializer, ConvenioSerializer, ContactoInteresSerializer, LinkInteresSerializer
from django.utils.translation import gettext_lazy as _
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.serializers import JWTSerializer
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from google.auth.transport import requests
from google.oauth2 import id_token
from backend_colmed.settings import GOOGLE_CLIENT_ID, EMAIL_HOST_USER
from base_colmed.authentication import CookieJWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from .utils import send_push_notification
from django.core.mail import EmailMultiAlternatives




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
        """Endpoint para obtener todos los eventos."""
        eventos = Evento.objects.all().order_by('-fecha_inicio').exclude(privado=True)
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def eventos_base_app(self, request):
        """Endpoint para obtener todos los eventos."""
        eventos = Evento.objects.all().order_by('-fecha_inicio').exclude(activo=False)
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data)
    
class PublicidadMedicaViewSet(viewsets.ModelViewSet):
    queryset = PublicidadMedica.objects.all()
    serializer_class = PublicidadMedicaSerializer

    @action(detail=False, methods=['get'])
    def publicidades_base(self, request):
        """Endpoint para obtener todas las publicidades medicas activas."""
        publicidades = PublicidadMedica.objects.filter(activo=True).order_by('-fecha_modificacion')
        serializer = self.get_serializer(publicidades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def todas_publicidades(self, request):
        """Endpoint para obtener todas las publicidades medicas."""
        publicidades = PublicidadMedica.objects.all().order_by('-fecha_modificacion')
        serializer = self.get_serializer(publicidades, many=True)
        return Response(serializer.data)
    
class ContactoInteresViewSet(viewsets.ModelViewSet):
    queryset = ContactoInteres.objects.all()
    serializer_class = ContactoInteresSerializer

    @action(detail=False, methods=['get'])
    def contactos_publicos(self, request):
        """Endpoint para obtener todas contactos publicos."""
        contactos = ContactoInteres.objects.filter(privado=False)
        serializer = self.get_serializer(contactos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def contactos_privados(self, request):
        """Endpoint para obtener todos los contactos privados"""
        contactos = ContactoInteres.objects.filter(privado=True)
        serializer = self.get_serializer(contactos, many=True)
        return Response(serializer.data)
    
class LinkInteresViewSet(viewsets.ModelViewSet):
    queryset = LinkInteres.objects.all()
    serializer_class = LinkInteresSerializer

    @action(detail=False, methods=['get'])
    def todos_links(self, request):
        """Endpoint para obtener todas contactos publicos."""
        links = LinkInteres.objects.order_by('orden')
        serializer = self.get_serializer(links, many=True)
        return Response(serializer.data)
    
    # @action(detail=False, methods=['get'])
    # def contactos_privados(self, request):
    #     """Endpoint para obtener todos los contactos privados"""
    #     contactos = ContactoInteres.objects.filter(privado=True)
    #     serializer = self.get_serializer(contactos, many=True)
    #     return Response(serializer.data)
    
@method_decorator(csrf_exempt, name='dispatch')
class EventoCreateUpdateView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        """
        Endpoint para crear o actualizar un evento.
        Si el autor está presente en el request, se actualiza el evento existente.
        Si el autor no está presente, se crea un nuevo evento.
        """
        data = request.data.copy()
        autor_id = data.get('autor')
        
        try:
            autor = User.objects.get(id=autor_id) if autor_id else request.user
        except User.DoesNotExist:
            return Response({"detail": "Autor no válido."}, status=status.HTTP_400_BAD_REQUEST)        

        if data.get('id'):
            # Actualizar la noticia existente
            try:
                evento = Evento.objects.get(id=data.get('id'))
                data['autor'] = int(autor_id)
                serializer = EventoSerializer(evento, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Evento.DoesNotExist:
                return Response({"detail": "Evento no encontrada para el autor especificado."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Crear una nueva noticia
            # data['autor'] = request.user.id
            data['autor'] = int(autor_id)
            serializer = EventoSerializer(data=data)
            if serializer.is_valid():
                evento = serializer.save()

                # Llamar al método para enviar notificación push
                self.send_event_notification(evento)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def send_event_notification(self, evento):
        # """
        # Envía una notificación push cuando se crea un nuevo evento.
        # """
        # title = "¡Nuevo Evento Colmed Aysén!"
        # body = "'" + str(evento.titulo) + "'"
        # data_payload = {"event_id": str(evento.id), "type": "nuevo_evento"}
        """
        Envía una notificación push cuando se crea un nuevo evento.
        El mensaje varía según si el evento es privado o público.
        """
        if evento.privado:
            title = "¡Evento para Colegiados - Colmed Aysén!"
            body = "Evento privado: " + str(evento.titulo)
            data_payload = {"event_id": str(evento.id), "type": "nuevo_evento_privado"}
        else:
            title = "¡Nuevo Evento Colmed Aysén!"
            body = "Evento público: " + str(evento.titulo)
            data_payload = {"event_id": str(evento.id), "type": "nuevo_evento_publico"}
        
        # Obtener los tokens de los dispositivos registrados
        tokens = list(
            MedicoAppMovil.objects.exclude(fcm_token__isnull=True)
                                 .exclude(fcm_token__exact="")
                                 .values_list('fcm_token', flat=True)
        )

        if tokens:
            response_push = send_push_notification(tokens, title, body, data_payload)
            # Opcional: imprimir o registrar la respuesta
            

@method_decorator(csrf_exempt, name='dispatch')
class PublicidadMedicaoCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        """
        Endpoint para crear o actualizar una publicidad médica.
        Si el autor está presente en el request, se actualiza una publicidad médica.
        Si el autor no está presente, se crea una publicidad médica.
        """
        data = request.data.copy()
        autor_id = data.get('autor')
        try:
            autor = User.objects.get(id=autor_id) if autor_id else request.user
        except User.DoesNotExist:
            return Response({"detail": "Autor no válido."}, status=status.HTTP_400_BAD_REQUEST)

        if data.get('id'):
            # Actualizar la noticia existente
            try:
                publicidad_medica = PublicidadMedica.objects.get(id=data.get('id'))
                data['autor'] = int(autor_id)
                serializer = PublicidadMedicaSerializer(publicidad_medica, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except PublicidadMedica.DoesNotExist:
                return Response({"detail": "Publicidad Medica no encontrada para el autor especificado."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Crear una nueva noticia
            data['autor'] = int(autor_id)
            serializer = PublicidadMedicaSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ConvenioViewSet(viewsets.ModelViewSet):
    queryset = Convenio.objects.all()
    serializer_class = ConvenioSerializer

    @action(detail=False, methods=['get'])
    def todos_convenios(self, request):
        # Obtener todos los convenios
        convenios = Convenio.objects.all()

        # Filtrar por tipo
        nacionales = convenios.filter(tipo='nacional')
        regionales = convenios.filter(tipo='regional')

        # Serializar los datos
        serializer_nacionales = ConvenioSerializer(nacionales, many=True, context={'request': request})
        serializer_regionales = ConvenioSerializer(regionales, many=True, context={'request': request})

        # Obtener la configuración (asumido que existe un único registro o se toma el primero)
        config = ConveniosConfig.objects.first()
        config_serializer = ConveniosConfigSerializer(config) if config else None

        data = {
            "nacionales": serializer_nacionales.data,
            "regionales": serializer_regionales.data,
        }
        if config_serializer:
            data["todos_convenios_link"] = config_serializer.data.get('todos_convenios_link')

        return Response(data)

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
            return Response({"detail": "User not authorized or not registered in the system"}, status=status.HTTP_401_UNAUTHORIZED)

        # Obtener perfiles del usuario
        perfiles = Perfil.objects.filter(user=user)
        perfiles_data = PerfilSerializer(perfiles, many=True).data

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # return Response({
        #     "access": access_token,
        #     "refresh": refresh_token,
        #     "user": {
        #         "username": user.username,
        #         "email": user.email,
        #         "perfiles": perfiles_data,
        #         "name_google" : name_google,
        #         "picture": picture_google
        #     }
        # }, status=status.HTTP_200_OK)
        # Construir la respuesta
        response_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "perfiles": perfiles_data,
                "name_google": name_google,
                "picture": picture_google
            }
        }
        response = Response(response_data, status=status.HTTP_200_OK)

        # Ajustar cookies con HttpOnly + Secure (según entorno)
        from django.conf import settings
        secure_cookie = not settings.DEBUG  # True en prod (HTTPS), False en dev
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=secure_cookie,
            samesite='None',  # asumiendo front/back en dominios distintos
            max_age=60*2,     # 2 minutos
            path='/'
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=secure_cookie,
            samesite='None',
            max_age=60*60*24*7,  # 7 días
            path='/'
        )

        return response

### USO APP MOVIL ###

class GoogleLoginMobile(APIView):
    """
    Recibe un id_token (credential) de Google, valida el token,
    verifica existencia del usuario en BD, genera tokens JWT propios.
    """
    def post(self, request):        
        
        id_token_google = request.data.get('id_token')
        fcm_token = request.data.get('fcm_token', None)

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


        # 1) Buscar en MedicoAppMovil
        try:
            medico_app_movil = MedicoAppMovil.objects.get(email=email)
            # De aquí podemos acceder al Medico y luego a su user si fuera necesario
            # user = medico_app_movil.medico.user  # si existe
            user = medico_app_movil.medico.user if medico_app_movil.medico else None
        except MedicoAppMovil.DoesNotExist:
            medico_app_movil = None
            user = None


        # 2) Si no lo encuentras en MedicoAppMovil, buscar en User
        if not medico_app_movil:
            try:
                user = User.objects.get(email=email)

                # Verificar si el usuario tiene un médico asociado
                medico = Medico.objects.filter(user=user).first()
        
                if medico:
                    # Es el primer inicio de sesión en la app móvil, registrar en MedicoAppMovil
                    medico_app_movil = MedicoAppMovil.objects.create(
                        medico=medico,
                        email=email,
                        contraseña=""  # Contraseña vacía porque usó Google Login
                    )
            except User.DoesNotExist:
                user = None

         # 3) Si no se encontró ni en MedicoAppMovil ni en User => 403
        if not medico_app_movil and not user:
            return Response(
                {"detail": "No registrado. Por favor provea su ICM para registro."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user is None:
            # En casos raros que tengamos MedicoAppMovil sin user. 
            # Generar un user "dummy"? O no requerir user en tu sistema?
            return Response(
                {"detail": "El registro en MedicoAppMovil no tiene usuario asociado."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Actualizar fcm_token si se proporcionó
        if fcm_token:
            medico_app_movil.fcm_token = fcm_token
            medico_app_movil.save()


        # Obtener perfiles del usuario
        perfiles = Perfil.objects.filter(user=user)
        perfiles_data = PerfilSerializer(perfiles, many=True).data

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "perfiles": perfiles_data,
                "name_google": name_google,
                "picture": picture_google
            }
        }
        response = Response(response_data, status=status.HTTP_200_OK)

        # Ajustar cookies con HttpOnly + Secure (según entorno)
        from django.conf import settings
        secure_cookie = not settings.DEBUG  # True en prod (HTTPS), False en dev
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=secure_cookie,
            samesite='None',  # asumiendo front/back en dominios distintos
            max_age=60*2,     # 2 minutos
            path='/'
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=secure_cookie,
            samesite='None',
            max_age=60*60*24*7,  # 7 días
            path='/'
        )

        return response


class RegisterMedicoAppMovilView(APIView):
    """
    Endpoint que recibe:
      - icm
      - email
      - password
    Valida si el icm existe en Medico.
      - Si existe y no tiene un MedicoAppMovil asociado con ese email, lo crea.
      - Si ya existe un MedicoAppMovil con ese email, retornaría error indicando que ya existe.
      - Si el icm no existe en Medico => error.
    """
    def post(self, request):
        icm = request.data.get("icm")
        email = request.data.get("email")
        password = request.data.get("password")

        if not icm or not email or not password:
            return Response(
                {"detail": "Todos los campos (icm, email, password) son requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar si el icm existe en Medico
        try:
            medico_obj = Medico.objects.get(icm=icm)
        except Medico.DoesNotExist:
            return Response(
                {"detail": "ICM no registrado en el sistema."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar si ya existe un MedicoAppMovil con ese email 
        # (podrías verificar también si coincide con el mismo medico)
        # if MedicoAppMovil.objects.filter(email=email).exists():
        #     return Response(
        #         {"detail": "Ya existe un registro con este email en MedicoAppMovil."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # # Crear el registro
        # medico_app_movil = MedicoAppMovil.objects.create(
        #     medico=medico_obj,
        #     email=email,
        #     contraseña=""  # Se setea vacía y luego se usa set_password
        # )
        # # Guardar la contraseña hasheada
        # medico_app_movil.set_password(password)
        
        # return Response({"detail": "Registro creado exitosamente."}, 
        #                 status=status.HTTP_201_CREATED)

        try:
            # Intentar obtener un registro existente en MedicoAppMovil para el email dado
            medico_app = MedicoAppMovil.objects.get(email=email)
            # Si ya tiene contraseña (es decir, password no está vacío), se retorna error.
            
            if medico_app.contraseña:
                return Response(
                    {"detail": "Ya existe un registro con este email en MedicoAppMovil."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Si existe pero la contraseña está vacía, actualizamos el registro.
                medico_app.set_password(password)
                medico_app.save()
                return Response(
                    {"detail": "Registro actualizado exitosamente."},
                    status=status.HTTP_200_OK
                )
        except MedicoAppMovil.DoesNotExist:
            # Crear un nuevo registro
            medico_app = MedicoAppMovil.objects.create(
                medico=medico_obj,
                email=email,
                contraseña=""  # Se inicializa vacío; luego se setea mediante set_password
            )
            medico_app.set_password(password)
            medico_app.save()
            return Response(
                {"detail": "Registro creado exitosamente."},
                status=status.HTTP_201_CREATED
            )

class LoginMedicoAppMovilView(APIView):
    """
    Permite login con email y password para quienes ya tienen su MedicoAppMovil creado.
    1) Se busca en MedicoAppMovil por email
    2) Se compara la password
    3) Si ok => generar tokens JWT 
    """
    def post(self, request):
        icm = request.data.get('icm')
        password = request.data.get('password')
        fcm_token = request.data.get('fcm_token', None)

        if not icm or not password:
            return Response({"detail": "ICM y contraseña requeridos."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # medico = Medico.objects.get(icm=icm)
            medico_app_movil = MedicoAppMovil.objects.get(medico__icm=icm)
        except MedicoAppMovil.DoesNotExist:
            return Response({"detail": "Credenciales inválidas."},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Validar password
        from django.contrib.auth.hashers import check_password
        if not check_password(password, medico_app_movil.contraseña):
            return Response({"detail": "Contraseña incorrecta."}, 
                            status=status.HTTP_401_UNAUTHORIZED)


        # Actualizar fcm_token si se proporcionó
        if fcm_token and medico_app_movil.fcm_token!="":
            medico_app_movil.fcm_token = fcm_token
            medico_app_movil.save()

        # Aquí se asume que el MedicoAppMovil podría estar enlazado a un User 
        # o no, dependiendo de tu modelo. Si deseas emitir tokens JWT
        # basados en un user real, tendrías que enlazar 'medico_app_movil.medico.user'.
        user = medico_app_movil.medico.user if medico_app_movil.medico else None
        if user is None:
            return Response(
                {"detail": "No existe un User asociado a este Medico. (Opcional)"},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Obtener perfiles del usuario
        perfiles = Perfil.objects.filter(user=user)
        perfiles_data = PerfilSerializer(perfiles, many=True).data

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "perfiles": perfiles_data,
                "name_google": None,
                "picture": None
            }
        }
        response = Response(response_data, status=status.HTTP_200_OK)

        # Ajustar cookies con HttpOnly + Secure (según entorno)
        from django.conf import settings
        secure_cookie = not settings.DEBUG  # True en prod (HTTPS), False en dev
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=secure_cookie,
            samesite='None',  # asumiendo front/back en dominios distintos
            max_age=60*2,     # 2 minutos
            path='/'
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=secure_cookie,
            samesite='None',
            max_age=60*60*24*7,  # 7 días
            path='/'
        )

        return response

        # Generar tokens
        # refresh = RefreshToken.for_user(user)
        # access_token = str(refresh.access_token)
        # refresh_token = str(refresh)

        # return Response({
        #     "detail": "Login exitoso.",
        #     "access": access_token,
        #     "refresh": refresh_token,
        #     "user_id": user.id
        # }, status=status.HTTP_200_OK)


class RequestPasswordResetView(APIView):
    """
    Recibe 'identifier' que puede ser un email o un icm.
    1) Busca el registro en MedicoAppMovil (por email o por medico__icm).
    2) Crea un token de reseteo.
    3) Envía un email con un link simple y explicativo.
    """
    def post(self, request):
        identifier = request.data.get("identifier")
        if not identifier:
            return Response(
                {"detail": _("Debes proporcionar tu email o tu ICM.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 1) Buscar en MedicoAppMovil. Intentar como email:
        try:
            medico_app_movil = MedicoAppMovil.objects.get(email=identifier)
        except MedicoAppMovil.DoesNotExist:
            medico_app_movil = None

        # Si no se encontró por email, intentamos buscar por icm (en el modelo Medico)
        if not medico_app_movil:
            try:
                medico = Medico.objects.get(icm=identifier)
                medico_app_movil = MedicoAppMovil.objects.get(medico=medico)
            except (Medico.DoesNotExist, MedicoAppMovil.DoesNotExist):
                # No existe por email ni por icm
                # Por seguridad, puedes responder genérico o especial.
                return Response(
                    {"detail": _("No se encontró un registro asociado a ese email o ICM en las bases de Colmed Aysén.")},
                    status=status.HTTP_404_NOT_FOUND
                )

        # 2) Crear token de reseteo
        reset_token = PasswordResetToken.objects.create(medico_app_movil=medico_app_movil)

        # 3) Enviar email.  
        # Asumimos que medico_app_movil.email es el correo real.
        user_email = medico_app_movil.email
        
        # Construye el link: la idea es que el front reciba el token y muestre un form
        #reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
        reset_link = f"http://localhost:8080/#/colmed/confirm-pass-reset?token={reset_token.token}"        

        text_content = (
            "Hola,\n\n"
            "Recibimos una solicitud para restablecer tu contraseña.\n\n"
            f"Por favor visita el siguiente enlace para establecer una nueva contraseña:\n{reset_link}\n\n"
            "Si no solicitaste este cambio, ignora este mensaje.\n\n"
            "Saludos,\nEl equipo de Colmed Aysén."
        )

        message = (
            "Hola,\n\n"
            "Recibimos una solicitud para restablecer tu contraseña.\n\n"
            f"Por favor haz clic en el siguiente enlace para establecer una nueva contraseña:\n{reset_link}\n\n"
            "Si no solicitaste este cambio, ignora este mensaje.\n\n"
            "Saludos,\nEl equipo de soporte."
        )

        html_content = f"""
            <p>Hola,</p>
            <p>Recibimos una solicitud para restablecer tu contraseña.</p>
            <p>Haz clic en el siguiente enlace para establecer una nueva contraseña:</p>
            <p><a href="{reset_link}" style="padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Restablecer contraseña</a></p>
            <p>Si no solicitaste este cambio, ignora este mensaje.</p>
            <p>Saludos,<br>El equipo de Colmed Aysén.</p>
        """
        try:
            # send_mail(
            #     subject=subject,
            #     message=message,
            #     from_email=EMAIL_HOST_USER,
            #     recipient_list=[user_email],
            #     fail_silently=False,
            # )
            self.send_reset_email(user_email, reset_link)
        except Exception as e:
            return Response({"detail": _("Error al enviar el correo. Intenta de nuevo.")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {"detail": _("Se ha enviado un correo con instrucciones para restablecer tu contraseña.")},
            status=status.HTTP_200_OK
        )
    
    def send_reset_email(self, user_email, reset_link):
        
        subject = "Restablecimiento de contraseña APP Colmed Aysén"
        text_content = (
            "Hola,\n\n"
            "Recibimos una solicitud para restablecer tu contraseña.\n\n"
            f"Por favor visita el siguiente enlace para establecer una nueva contraseña:\n{reset_link}\n\n"
            "Si no solicitaste este cambio, ignora este mensaje.\n\n"
            "Saludos,\nEquipo de Colmed Aysén."
        )
        html_content = f"""\
            <div style="font-family: Arial, sans-serif;">
              <p>Hola,</p>
              <p>Recibimos una solicitud para restablecer tu contraseña.</p>
              <p>Haz clic en el siguiente enlace para establecer una nueva contraseña:</p>
              <p>
                <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 5px;">
                  Restablecer contraseña
                </a>
              </p>
              <p>Si no solicitaste este cambio, ignora este mensaje.</p>
              <p>Saludos,<br><b>Equipo de Colmed Aysén.</b></p>
            </div>
            """
        from django.core.mail import EmailMultiAlternatives
        msg = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [user_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

class ConfirmPasswordResetView(APIView):
    """
    Confirmación de reseteo de contraseña:
    - Recibe token y new_password
    - Valida que el token exista, no esté usado y no esté expirado
    - Actualiza la contraseña en MedicoAppMovil
    """
    def post(self, request):
        token_str = request.data.get("token")
        new_password = request.data.get("new_password")

        if not token_str or not new_password:
            return Response(
                {"detail": _("Faltan datos: token y/o nueva contraseña.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar token
        try:
            reset_token = PasswordResetToken.objects.get(token=token_str, used=False)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": _("Token inválido o ya utilizado.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Revisar expiración
        if reset_token.is_expired():
            return Response({"detail": _("El enlace ha expirado. Por favor solicita un nuevo enlace de reseteo en 'Recuperar Contraseña'.")},
                            status=status.HTTP_400_BAD_REQUEST)

        # Actualizar contraseña
        medico_app_movil = reset_token.medico_app_movil
        medico_app_movil.contraseña = make_password(new_password)
        medico_app_movil.save()

        # Marcar token como usado
        reset_token.used = True
        reset_token.save()

        return Response(
            {"detail": _("La contraseña ha sido restablecida exitosamente.")},
            status=status.HTTP_200_OK
        )
    
class ChangePasswordView(APIView):
    """
    Cambia contraseña cuando el usuario está logueado.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"detail": _("Contraseña antigua y nueva son requeridas.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
    
        try:
            medico = user.medico
            medico_app_movil = MedicoAppMovil.objects.get(medico=medico)
        except (AttributeError, MedicoAppMovil.DoesNotExist):
            return Response(
                {"detail": _("No se encontró un registro MedicoAppMovil para este usuario.")},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar la contraseña antigua
        if not check_password(old_password, medico_app_movil.contraseña):
            return Response({"detail": _("La contraseña antigua es incorrecta.")},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Chequear que la nueva no sea igual
        if check_password(new_password, medico_app_movil.contraseña):
            return Response(
                {"detail": _("La nueva contraseña no puede ser la misma que la anterior.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar la contraseña
        medico_app_movil.contraseña = make_password(new_password)
        medico_app_movil.save()

        return Response({"detail": _("Contraseña cambiada exitosamente.")},
                        status=status.HTTP_200_OK)

class RefreshTokenView(APIView):
    """
    Endpoint para refrescar el token de acceso usando la cookie refresh_token.
    """
    def post(self, request):
        refresh_cookie = request.COOKIES.get('refresh_token')
        if not refresh_cookie:
            return Response({"detail": "No refresh cookie provided."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_cookie)
            new_access_token = str(refresh.access_token)

            # (Opcional) Rotar refresh token si quieres emitir uno nuevo
            # new_refresh_token = str(RefreshToken.for_user(refresh.user))

            response_data = {"detail": "Access token refreshed."}
            response = Response(response_data, status=status.HTTP_200_OK)

            # Setear de nuevo la cookie access_token
            from django.conf import settings
            secure_cookie = not settings.DEBUG
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=secure_cookie,
                samesite='None',
                max_age=60*2,  # ej. 2 minutos
                path='/'
            )

            # Si rota refresh token, setearlo también
            # response.set_cookie(
            #     key='refresh_token',
            #     value=new_refresh_token,
            #     httponly=True,
            #     secure=secure_cookie,
            #     samesite='None',
            #     max_age=60*60*24*7,
            #     path='/'
            # )

            return response

        except Exception:
            return Response({"detail": "Invalid or expired refresh token."},
                            status=status.HTTP_401_UNAUTHORIZED)


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