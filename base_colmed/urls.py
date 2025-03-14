from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BeneficioViewSet, PlazaViewSet, EventoViewSet, PerfilViewSet, user_profile, LoginView, UpdatePasswordView, EventoCreateUpdateView, PublicidadMedicaoCreateUpdateView, PublicidadMedicaViewSet, GoogleLoginMobile,LoginMedicoAppMovilView, RegisterMedicoAppMovilView, ConvenioViewSet, ContactoInteresViewSet, LinkInteresViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'beneficios', BeneficioViewSet, basename='beneficios')
router.register(r'plazas', PlazaViewSet, basename='plazas')
router.register(r'eventos', EventoViewSet, basename='eventos')
router.register(r'perfiles', PerfilViewSet, basename='perfiles')
router.register(r'publicidades', PublicidadMedicaViewSet, basename='publicidades')
router.register(r'convenios', ConvenioViewSet, basename='convenios')
router.register(r'contactos', ContactoInteresViewSet, basename='contactos')
router.register(r'links', LinkInteresViewSet, basename='links')

#urlpatterns = router.urls
urlpatterns = router.urls + [
    path('profile/', user_profile, name='user-profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('update-password/', UpdatePasswordView.as_view(), name='update-password'),
    
    # Endpoints para obtener y refrescar tokens
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Para obtener el token (access y refresh)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Para refrescar el access token
    path('evento-create-update/', EventoCreateUpdateView.as_view(), name='evento-create-update'),  
    path('publicidad-create-update/', PublicidadMedicaoCreateUpdateView.as_view(), name='publicidad-create-update'),  
]
