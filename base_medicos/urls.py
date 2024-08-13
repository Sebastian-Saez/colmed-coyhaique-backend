from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicoViewSet, CuotaViewSet

router = DefaultRouter()
router.register(r'medicos', MedicoViewSet, basename='medicos')
router.register(r'cuotas', CuotaViewSet, basename='cuotas')

urlpatterns = router.urls
