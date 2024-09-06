from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BeneficioViewSet, PlazaViewSet, EventoViewSet, PerfilViewSet, user_profile, LoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'beneficios', BeneficioViewSet, basename='beneficios')
router.register(r'plazas', PlazaViewSet, basename='plazas')
router.register(r'eventos', EventoViewSet, basename='eventos')
router.register(r'perfiles', PerfilViewSet, basename='perfiles')

#urlpatterns = router.urls
urlpatterns = router.urls + [
    path('profile/', user_profile, name='user-profile'),
    path('login/', LoginView.as_view(), name='login'),
    # Endpoints para obtener y refrescar tokens
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Para obtener el token (access y refresh)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Para refrescar el access token
]
