from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MisionVisionViewSet, NormativaViewSet, DirectivaViewSet,
    DepartamentoViewSet, AgrupacionRegionalViewSet, CapituloViewSet,
    TribunalEticaViewSet, SomosCreateUpdateAPIView,
    PaymentInfoViewSet, ColegiarseInfoViewSet, CasaMedicoInfoViewSet
)

router = DefaultRouter()
router.register(r'toolbar/misionvision', MisionVisionViewSet, basename='misionvision')
router.register(r'toolbar/normativa', NormativaViewSet, basename='normativa')
router.register(r'toolbar/directiva', DirectivaViewSet, basename='directiva')
router.register(r'toolbar/departamentos', DepartamentoViewSet, basename='departamentos')
router.register(r'toolbar/agrupaciones', AgrupacionRegionalViewSet, basename='agrupaciones')
router.register(r'toolbar/capitulos', CapituloViewSet, basename='capitulos')
router.register(r'toolbar/tribunal_etica', TribunalEticaViewSet, basename='tribunal')
router.register(r'toolbar/pagos', PaymentInfoViewSet, basename='pagos')
router.register(r'toolbar/casa_medico', CasaMedicoInfoViewSet, basename='casa_medico')
router.register(r'toolbar/colegiarse', ColegiarseInfoViewSet, basename='colegiarse')

urlpatterns = router.urls + [
    # path('api/', include(router.urls)),
    path('toolbar-create-update/<str:section>/', SomosCreateUpdateAPIView.as_view(), name='somos-create-update'),
]