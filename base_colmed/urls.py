from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BeneficioViewSet, PlazaViewSet, EventoViewSet, PerfilViewSet

router = DefaultRouter()
router.register(r'beneficios', BeneficioViewSet, basename='beneficios')
router.register(r'plazas', PlazaViewSet, basename='plazas')
router.register(r'eventos', EventoViewSet, basename='eventos')
router.register(r'perfiles', PerfilViewSet, basename='perfiles')

urlpatterns = router.urls
