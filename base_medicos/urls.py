from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicoViewSet, CuotaViewSet, ProcesarRegistrosSuperintendenciaAPIView, RegistroSuperintendenciaViewSet, InstitucionViewSet, EspecialidadViewSet, OrdenProfesionalViewSet, ProcesarRegistrosSR

router = DefaultRouter()
router.register(r'medicos', MedicoViewSet, basename='medicos')
router.register(r'superintendencia', RegistroSuperintendenciaViewSet, basename='superintendencia')
router.register(r'institucion', InstitucionViewSet, basename='institucion')
router.register(r'especialidades', EspecialidadViewSet, basename='especialidades')
router.register(r'profesiones', OrdenProfesionalViewSet, basename='profesiones')
router.register(r'cuotas', CuotaViewSet, basename='cuotas')

urlpatterns = router.urls + [
    path('procesar-registros-superintendencia/', ProcesarRegistrosSuperintendenciaAPIView.as_view(), name='procesar_registros_superintendencia'),
    path('procesar-registros-sr/', ProcesarRegistrosSR.as_view(), name='procesar-registros-sr'),
]
